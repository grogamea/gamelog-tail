# Level-Range Filter

The `level_range_filter` lets you keep only log entries whose severity falls
within a configurable **minimum / maximum** band.

## Severity order

From lowest to highest:

```
debug  <  info  <  warning  <  error  <  critical
```

## Usage

```python
from gamelog_tail.filters_level import level_range_filter

# Keep only warnings and errors (exclude debug, info, critical)
f = level_range_filter(min_level="warning", max_level="error")

filtered = list(f(iter(log_entries)))
```

### Arguments

| Argument    | Type  | Default      | Description                              |
|-------------|-------|--------------|------------------------------------------|
| `min_level` | `str` | `"debug"`    | Lowest severity to include (inclusive).  |
| `max_level` | `str` | `"critical"` | Highest severity to include (inclusive). |

Both arguments are **case-insensitive**.

### Errors

`ValueError` is raised when:
- An unrecognised level name is supplied.
- `min_level` has a higher rank than `max_level`.

## Integration with the pipeline

Pass the filter to `build_filters` / `run` like any other filter:

```python
from gamelog_tail.pipeline import run
from gamelog_tail.filters_level import level_range_filter

run(
    parser=parser,
    stream=stream,
    filters=[level_range_filter(min_level="warning")],
    formatter=formatter,
    out=sys.stdout,
)
```

## Entries with unknown levels

Entries whose `level` field is `None` or contains an unrecognised string are
**always passed through** so that no information is silently lost.
