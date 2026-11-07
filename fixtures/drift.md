# Deliberately stale example

This negative control must fail: the example prints 5 while the docs promise 4.

```python check=stale-output
print(2 + 3)
```

```text expect=stale-output
4
```
