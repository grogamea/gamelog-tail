# Transform Filters

Transform filters mutate log entries rather than simply passing or blocking them.
All three transforms are composable and can be combined with any other filter in
the pipeline.

## `truncate_message_filter(max_length)`

Truncates the `message` field to at most `max_length` characters, appending `…`
when truncation occurs.  Entries whose messages are already short enough are
returned unchanged (same object).

```python
from gamelog_tail.filters_transform import truncate_message_filter

f = truncate_message_filter(80)
result = f(entry)   # message capped at 80 chars
```

**Raises** `ValueError` if `max_length < 1`.

---

## `redact_pattern_filter(pattern, replacement="[REDACTED]")`

Replaces every match of the regular expression `pattern` inside the `message`
field with `replacement`.  Entries with no match are returned unchanged (same
object).

```python
from gamelog_tail.filters_transform import redact_pattern_filter

f = redact_pattern_filter(r"password=\S+", replacement="password=***")
result = f(entry)
```

**Raises** `ValueError` if `pattern` is an empty string.

---

## `tag_source_filter(tag, separator=":")`

Prepends `tag` to the `source` field using `separator`.  If the entry has no
source the tag is used as-is.

```python
from gamelog_tail.filters_transform import tag_source_filter

f = tag_source_filter("production", separator="/")
result = f(entry)   # source becomes e.g. "production/Renderer"
```

**Raises** `ValueError` if `tag` is an empty string.

---

## Integration helper

`build_transform_filters` and `apply_transform_filters` in
`gamelog_tail.filters_transform_integration` make it easy to wire these
transforms from CLI arguments or configuration dictionaries:

```python
from gamelog_tail.filters_transform_integration import (
    build_transform_filters,
    apply_transform_filters,
)

filters = build_transform_filters(
    truncate=120,
    redact_patterns=[r"\d{4}-\d{4}-\d{4}-\d{4}"],  # credit card numbers
    tag="staging",
)

processed = apply_transform_filters(filters, entry)
if processed is not None:
    print(processed)
```
