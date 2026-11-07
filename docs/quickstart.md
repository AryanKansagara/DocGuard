# Quickstart

This reviewed example exercises JSON decoding and output checking.

```python check=json-example
import json
record = json.loads('{"name":"Ada","active":true}')
print(record['name'], record['active'])
```

```text expect=json-example
Ada True
```

## Summing a batch

```python check=sum-example
print(sum([2, 3, 5]))
```

```text expect=sum-example
10
```

[Local section](#summing-a-batch)
