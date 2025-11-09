# AsyncAPI Discovery Examples

This directory contains examples demonstrating how to use the AsyncAPI Discovery tool.

## Examples

### simple_usage.py

A basic example showing how to:
- Create a sample repository with event producers
- Initialize the AsyncAPI Discovery tool
- Discover event producers in the repository
- Generate an AsyncAPI specification
- Save the specification to a file

**Run the example:**
```bash
python examples/simple_usage.py
```

## Creating Your Own Examples

To use AsyncAPI Discovery in your own projects:

1. **Install the package:**
   ```bash
   pip install asyncapi-discovery
   ```

2. **Import and initialize:**
   ```python
   from asyncapi_discovery import AsyncAPIDiscovery
   
   discovery = AsyncAPIDiscovery('/path/to/repository')
   ```

3. **Discover producers:**
   ```python
   producers = discovery.discover()
   ```

4. **Generate specification:**
   ```python
   spec = discovery.generate_spec(producers)
   ```

5. **Save to file:**
   ```python
   with open('asyncapi.yaml', 'w') as f:
       f.write(spec)
   ```

## Supported Event Producer Patterns

The tool recognizes these common patterns:

**Python:**
```python
publish("event.name", data)
send("event.name", data)
emit("event.name", data)
produce("event.name", data)
```

**JavaScript/TypeScript:**
```javascript
publish('event.name', data);
send('event.name', data);
emit('event.name', data);
produce('event.name', data);
```

**Java:**
```java
publish("event.name", data);
send("event.name", data);
produce("event.name", data);
```

**Go:**
```go
Publish("event.name", data)
Send("event.name", data)
Produce("event.name", data)
```

## More Information

For more information, see the main [README.md](../README.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).
