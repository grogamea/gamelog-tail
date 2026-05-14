# `filters_pattern_group` — Multi-Pattern Group Filter

Matches log entries against a **group of regular expressions** in a single
filter step, with optional source tagging on match.

## API

```python
from gamelog_tail.filters_pattern_group import pattern_group_filter

f = pattern_group_filter(
    patterns,          # Iterable[str] — one or more regex strings
    *,
    field="message",   # "message" | "source"
    label=None,        # Optional[str] — prefix added to source on match
    mode="allow",      # "allow" | "deny"
)
```

### Parameters

| Parameter  | Type              | Default      | Description |
|------------|-------------------|--------------|-------------|
| `patterns` | `Iterable[str]`   | *(required)* | Regular expressions; at least one required. |
| `field`    | `str`             | `"message"`  | Entry attribute to match against (`message` or `source`). |
| `label`    | `str \| None`     | `None`       | When set, matching entries in *allow* mode have their `source` prefixed with `[label]`. |
| `mode`     | `str`             | `"allow"`    | `"allow"` passes entries matching any pattern; `"deny"` blocks them. |

## Examples

### Allow only crash-related lines

```python
f = pattern_group_filter([r"crash", r"assert", r"fatal"])
```

### Block noisy subsystems by source

```python
f = pattern_group_filter(
    [r"^AudioMixer", r"^VSync"],
    field="source",
    mode="deny",
)
```

### Tag security-relevant entries

```python
f = pattern_group_filter(
    [r"auth", r"permission denied", r"token"],
    label="SECURITY",
)
# Passing entries will have source set to "[SECURITY] <original source>"
```

## Notes

- Patterns are compiled once at filter-creation time.
- Matching uses `re.search`, so patterns need not be anchored unless desired.
- `label` is silently ignored in `deny` mode (no entry is returned on match).
