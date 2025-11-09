#!/usr/bin/env python3
"""
Advanced Example: Schema Enrichment
Shows how to extract actual payload schemas from Java classes
"""

import re
import asyncio
from typing import Dict, Any, Optional, List


class JavaSchemaExtractor:
    """Extracts JSON schema from Java class definitions"""
    
    def __init__(self, sourcegraph_client):
        """
        Args:
            sourcegraph_client: SourceGraphClient instance
        """
        self.sg_client = sourcegraph_client
    
    async def enrich_schema(
        self,
        event_metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich event metadata with actual schema from Java class
        
        Args:
            event_metadata: Event metadata from detector
            
        Returns:
            Enriched schema or None if not found
        """
        message_type = event_metadata.get('message_type', '')
        if message_type == 'Unknown' or not message_type:
            return None
        
        repository = event_metadata.get('repository', '')
        
        # Search for the class definition
        query = f'repo:{repository} class {message_type} lang:java'
        results = await self.sg_client.search(query, limit=5)
        
        if not results:
            return None
        
        # Get the full file content
        best_match = results[0]
        file_content = await self.sg_client.get_file_content(
            repo=best_match['repository'],
            path=best_match['file_path']
        )
        
        if not file_content:
            return None
        
        # Extract schema from class
        return self._parse_java_class(file_content, message_type)
    
    def _parse_java_class(
        self,
        file_content: str,
        class_name: str
    ) -> Dict[str, Any]:
        """Parse Java class and extract JSON schema"""
        
        # Find class definition
        class_pattern = rf'class\s+{class_name}\s*(?:<[^>]+>)?\s*\{{'
        match = re.search(class_pattern, file_content)
        
        if not match:
            return None
        
        # Extract fields
        fields = self._extract_fields(file_content, match.end())
        
        # Build JSON schema
        schema = {
            "type": "object",
            "title": class_name,
            "description": f"Schema for {class_name}",
            "properties": {},
            "required": []
        }
        
        for field in fields:
            schema['properties'][field['name']] = self._java_type_to_json_schema(field)
            if not field.get('nullable', False):
                schema['required'].append(field['name'])
        
        return schema
    
    def _extract_fields(
        self,
        content: str,
        start_pos: int
    ) -> List[Dict[str, Any]]:
        """Extract field definitions from class body"""
        fields = []
        
        # Match field declarations
        field_pattern = r'(?:private|public|protected)?\s+(?:final\s+)?(\w+(?:<[\w\s,<>]+>)?)\s+(\w+)\s*;'
        
        for match in re.finditer(field_pattern, content[start_pos:]):
            java_type = match.group(1)
            field_name = match.group(2)
            
            fields.append({
                'name': field_name,
                'java_type': java_type,
                'nullable': 'Optional' in java_type or '@Nullable' in content[max(0, match.start()-50):match.start()]
            })
        
        return fields
    
    def _java_type_to_json_schema(self, field: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Java type to JSON Schema type"""
        java_type = field['java_type']
        
        # Type mapping
        type_map = {
            'String': {'type': 'string'},
            'Integer': {'type': 'integer'},
            'int': {'type': 'integer'},
            'Long': {'type': 'integer', 'format': 'int64'},
            'long': {'type': 'integer', 'format': 'int64'},
            'Double': {'type': 'number', 'format': 'double'},
            'double': {'type': 'number', 'format': 'double'},
            'Float': {'type': 'number', 'format': 'float'},
            'float': {'type': 'number', 'format': 'float'},
            'Boolean': {'type': 'boolean'},
            'boolean': {'type': 'boolean'},
            'BigDecimal': {'type': 'string', 'format': 'decimal'},
            'LocalDate': {'type': 'string', 'format': 'date'},
            'LocalDateTime': {'type': 'string', 'format': 'date-time'},
            'Instant': {'type': 'string', 'format': 'date-time'},
            'UUID': {'type': 'string', 'format': 'uuid'},
        }
        
        # Check for generic types
        if '<' in java_type:
            base_type = java_type.split('<')[0]
            if base_type in ['List', 'Set', 'Collection']:
                inner_type = re.search(r'<(.+)>', java_type).group(1)
                return {
                    'type': 'array',
                    'items': type_map.get(inner_type.strip(), {'type': 'object'})
                }
            elif base_type == 'Map':
                return {
                    'type': 'object',
                    'additionalProperties': True
                }
        
        # Return mapped type or default to object
        return type_map.get(java_type, {'type': 'object', 'description': f'Complex type: {java_type}'})


# Example usage with integration
async def demo_schema_enrichment():
    """Demonstrate schema enrichment"""
    
    print("=" * 80)
    print("Schema Enrichment Demo")
    print("=" * 80)
    print()
    
    # Mock event metadata
    event = {
        'service_name': 'payment-service',
        'repository': 'github.com/yourorg/payment-service',
        'channel_name': 'payment.processed',
        'message_type': 'PaymentProcessedEvent',
        'broker': 'kafka'
    }
    
    # Mock Java class content
    mock_java_class = """
    package com.company.payment.events;
    
    import java.time.Instant;
    import java.math.BigDecimal;
    import java.util.UUID;
    
    public class PaymentProcessedEvent {
        private UUID paymentId;
        private String customerId;
        private BigDecimal amount;
        private String currency;
        private Instant processedAt;
        private String paymentMethod;
        private String status;
    }
    """
    
    print(f"Event: {event['channel_name']}")
    print(f"Message Type: {event['message_type']}")
    print()
    print("Extracting schema from Java class...")
    print()
    
    # Parse the mock class
    extractor = JavaSchemaExtractor(None)  # None since we're using mock data
    schema = extractor._parse_java_class(mock_java_class, 'PaymentProcessedEvent')
    
    if schema:
        print("Extracted Schema:")
        print("-" * 80)
        import json
        print(json.dumps(schema, indent=2))
        print()
        print("✓ Schema successfully enriched with actual payload fields")
    else:
        print("✗ Could not extract schema")
    
    print()
    print("Integration Steps:")
    print("1. In event_detector.py: Extract message_type from code")
    print("2. In main.py: Call JavaSchemaExtractor.enrich_schema()")
    print("3. In asyncapi_generator.py: Use enriched schema instead of template")
    print()
    print("Benefits:")
    print("- Accurate payload documentation")
    print("- Automatic schema validation")
    print("- Better developer experience")
    print("- Contract testing support")
    print()


if __name__ == "__main__":
    asyncio.run(demo_schema_enrichment())