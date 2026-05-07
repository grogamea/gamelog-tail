# Keyword Filters

The `gamelog_tail.filters_keyword` module provides two plain-text keyword
filters that operate on the `message` field of a `LogEntry`.

## `keyword_allowlist_filter(keywords)`

Passes only entries whose message contains **at least one** of the supplied
keywords. Matching is case-insensitive and sub-string based.

```python
from gamelog_tail.filters_keyword import keyword_allowlist_filter

f = keyword_allowlist_filter(["crash", "fatal", "exception"])
# Only entries mentioning crash / fatal / exception will pass.
```

Raises `ValueError` if the keyword list is empty.

## `keyword_denylist_filter(keywords)`

Blocks any entry whose message contains **at least one** of the supplied
keywords. All other entries pass through.

```python
from gamelog_tail.filters_keyword import keyword_denylist_filter

f = keyword_denylist_filter(["verbose", "debug noise"])
# Entries containing those phrases are suppressed.
```

Raises `ValueError` if the keyword list is empty.

## CLI usage

Both filters are exposed through the `--keyword-allow` and `--keyword-deny`
flags (comma-separated):

```
gamelog-tail game.log --keyword-allow crash,fatal
gamelog-tail game.log --keyword-deny verbose,heartbeat
```

## Combining filters

Keyword filters compose naturally with other filters via `pipeline.build_filters`:

```python
from gamelog_tail.pipeline import build_filters

filters = build_filters(
    level="WARNING",
    keyword_allow=["physics", "collision"],
    keyword_deny=["heartbeat"],
)
```

## Notes

- Matching is **sub-string**, not whole-word.  
  `keyword_allowlist_filter(["err"])` will match `"error"`, `"stderr"`, etc.
- If you need pattern-based matching, use `filters.by_message_pattern` instead.
