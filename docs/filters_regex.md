# filters_regex

Provides regular-expression-based filters for `LogEntry` objects.

## Functions

### `regex_filter(pattern, *, field="message", flags=0)`

Returns a callable `(LogEntry) -> bool` that passes entries where the
specified field **matches** the given pattern.

| Parameter | Type  | Default     | Description                                      |
|-----------|-------|-------------|--------------------------------------------------|
| `pattern` | `str` | —           | Regular-expression pattern (must be non-empty).  |
| `field`   | `str` | `"message"` | Entry attribute to search: `message`, `level`, or `source`. |
| `flags`   | `int` | `0`         | Optional `re` module flags, e.g. `re.IGNORECASE`. |

**Raises**
- `ValueError` – if `pattern` is empty or `field` is not a recognised attribute.
- `re.error` – if `pattern` is not a valid regular expression.

#### Example

```python
import re
from gamelog_tail.filters_regex import regex_filter

# Keep only entries whose message contains a number
f = regex_filter(r"\d+")

# Case-insensitive match on level field
f = regex_filter(r"^warn", field="level", flags=re.IGNORECASE)
```

---

### `regex_exclude_filter(pattern, *, field="message", flags=0)`

The inverse of `regex_filter` — **drops** entries that match the pattern.

#### Example

```python
from gamelog_tail.filters_regex import regex_exclude_filter

# Drop verbose audio-system chatter
f = regex_exclude_filter(r"AudioManager", field="source")
```

---

## Integration with `pipeline.build_filters`

Both filters can be composed with any other filter in the pipeline:

```python
from gamelog_tail.pipeline import run
from gamelog_tail.filters_regex import regex_filter, regex_exclude_filter

filters = [
    regex_filter(r"Exception"),          # only exception lines
    regex_exclude_filter(r"NullRef"),     # but not NullRef spam
]

run(stream, parser, filters, formatter)
```
