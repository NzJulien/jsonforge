# Extended Examples

## Detect a breaking API change

```bash
jsonforge diff api_response_v1.json api_response_v2.json
```

## Validate CI config data

```bash
jsonforge infer config_samples/*.json -o config_schema.json
jsonforge validate new_config.json config_schema.json
```

## Use as a library in a test

```python
from jsonforge import infer_schema, validate

def test_api_response_shape():
    schema = infer_schema(known_good_samples)
    assert validate(live_response, schema).is_valid
```
