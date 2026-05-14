# Sliding-Window Count Filter

The **sliding-window count filter** enforces a strict rolling-rate cap on
log entries, grouped by a configurable key (`source` or `level`).  Unlike
the burst filter — which suppresses output *after* a burst is detected and
then waits for a quiet period — this filter allows at most **N** entries
per key within any rolling time window of **W** seconds.

## API

```python
from gamelog_tail.filters_window import sliding_window_filter

f = sliding_window_filter(
    max_count=5,        # maximum entries allowed per key per window
    window_seconds=10.0,  # rolling window length in seconds
    key="source",       # group by: "source" (default) or "level"
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_count` | `int` | — | Maximum entries to pass per bucket per window. Must be ≥ 1. |
| `window_seconds` | `float` | — | Rolling window length in seconds. Must be > 0. |
| `key` | `str` | `"source"` | Bucket key — `"source"` or `"level"`. |

### Raises

- `ValueError` — if `max_count < 1`, `window_seconds <= 0`, or `key` is
  not `"source"` or `"level"`.

## Integration helper

```python
from gamelog_tail.filters_window_integration import (
    build_window_filters,
    apply_window_filters,
)

filters = build_window_filters(
    max_count=5,
    window_seconds=10.0,
    key="source",
)
survivors = apply_window_filters(entries, filters)
```

`build_window_filters` returns an empty list when either `max_count` or
`window_seconds` is `None`, making it safe to call unconditionally from
CLI argument parsing code.

## Example

```python
from gamelog_tail.filters_window import sliding_window_filter

# Allow at most 3 log lines per source every 5 seconds.
f = sliding_window_filter(3, 5.0, key="source")

for entry in stream:
    if f(entry):
        print(entry)
```
