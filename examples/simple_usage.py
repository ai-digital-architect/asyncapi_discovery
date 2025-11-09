"""
Simple usage example for AsyncAPI Discovery.

This example demonstrates how to use AsyncAPI Discovery to scan a repository
and generate AsyncAPI specifications.
"""

from asyncapi_discovery import AsyncAPIDiscovery
import tempfile
from pathlib import Path


def create_sample_repository():
    """Create a sample repository with event producers."""
    tmpdir = tempfile.mkdtemp()
    
    # Create a Python file with event producers
    python_file = Path(tmpdir) / "user_service.py"
    python_file.write_text("""
def create_user(username, email):
    user = {"username": username, "email": email}
    publish("user.created", user)
    return user

def update_user(user_id, data):
    updated_user = {"id": user_id, "data": data}
    emit("user.updated", updated_user)
    return updated_user

def delete_user(user_id):
    send("user.deleted", {"id": user_id})
""")
    
    # Create a JavaScript file with event producers
    js_file = Path(tmpdir) / "order_service.js"
    js_file.write_text("""
function placeOrder(orderId, items) {
    const order = { id: orderId, items: items };
    publish('order.placed', order);
    return order;
}

function cancelOrder(orderId) {
    send('order.cancelled', { id: orderId });
}
""")
    
    return tmpdir


def main():
    """Run the example."""
    print("AsyncAPI Discovery - Simple Usage Example")
    print("=" * 50)
    
    # Create a sample repository
    repo_path = create_sample_repository()
    print(f"\n1. Created sample repository at: {repo_path}")
    
    # Initialize discovery
    discovery = AsyncAPIDiscovery(repo_path)
    print("\n2. Initialized AsyncAPI Discovery")
    
    # Discover event producers
    producers = discovery.discover()
    print(f"\n3. Discovery complete!")
    print(f"   - Files scanned: {producers['statistics']['total_files_scanned']}")
    print(f"   - Producers found: {producers['statistics']['producers_found']}")
    print(f"\n   Discovered events:")
    for event in producers['events']:
        print(f"   - {event['name']} (in {Path(event['file']).name})")
    
    # Generate AsyncAPI specification
    spec = discovery.generate_spec(producers)
    print(f"\n4. Generated AsyncAPI specification ({len(spec)} characters)")
    
    # Save to file
    output_file = Path(repo_path) / "asyncapi.yaml"
    output_file.write_text(spec)
    print(f"\n5. Saved specification to: {output_file}")
    
    print("\nGenerated AsyncAPI Specification:")
    print("-" * 50)
    print(spec)
    print("-" * 50)
    
    print("\n✓ Example completed successfully!")
    
    # Cleanup
    import shutil
    shutil.rmtree(repo_path)
    print(f"\nCleaned up temporary directory: {repo_path}")


if __name__ == "__main__":
    main()
