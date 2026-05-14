# Context Window Filter

The **context window filter** emits a configurable number of log entries
before and after any entry that matches a *trigger* predicate.  This is
useful for understanding the events surrounding an error or warning without
showing the entire log stream.

## Core API

```python
from gamelog_tail.filters_context import context_window_filter

f = context_window_filter(predicate, before=2, after=2)
filtered = list(f(entries))
```

### Parameters

| Parameter   | Type                          | Default | Description                              |
|-------------|-------------------------------|---------|------------------------------------------|
| `predicate` | `Callable[[LogEntry], bool]`  | —       | Returns `True` for trigger entries.      |
| `before`    | `int`                         | `2`     | Lines of pre-context to include.         |
| `after`     | `int`                         | `2`     | Lines of post-context to include.        |

Both `before` and `after` must be `>= 0`; a `ValueError` is raised otherwise.

## Integration helpers

`build_context_filters` constructs a filter from high-level criteria
(level string and/or message regex pattern) suitable for use in the CLI
or pipeline:

```python
from gamelog_tail.filters_context_integration import (
    build_context_filters,
    apply_context_filters,
)

filters = build_context_filters(level="ERROR", pattern="crash", before=3, after=3)
result  = apply_context_filters(entries, filters)
```

If **either** `level` or `pattern` matches an entry, that entry acts as a
trigger.  If neither argument is supplied, an empty list is returned and
no filtering takes place.

## Behaviour notes

- Pre-context entries are buffered in a sliding window; only the most
  recent `before` entries are kept at any time.
- When two triggers appear close together their context windows are merged
  seamlessly — no entries are duplicated.
- An empty stream produces an empty output.
