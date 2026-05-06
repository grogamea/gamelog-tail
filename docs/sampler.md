# Log Entry Sampler

The **sampler** module provides a way to reduce log noise by forwarding only
every *N*-th entry that shares the same `(source, level)` bucket.  This is
useful when a game engine floods stdout with thousands of identical debug lines
per second and you only need a representative sample.

## Quick start

```python
from gamelog_tail.filters_sample import sample_filter
from gamelog_tail.pipeline import build_filters, run

# Keep 1 in every 20 DEBUG entries per source
filters = build_filters(extra=[sample_filter(rate=20)])
run(parser, stream, filters, formatter)
```

## API

### `Sampler(rate=10)`

Stateful class that tracks per-bucket counters.

| Method | Description |
|---|---|
| `should_keep(entry)` | Returns `True` for the 1st, (rate+1)-th, (2*rate+1)-th … entry in a bucket. |
| `reset()` | Clears all counters — useful between log sessions. |

### `sample_filter(rate=10) -> Callable`

Convenience factory that wraps a `Sampler` in a single-argument callable
suitable for use in the `gamelog_tail` pipeline.

The returned function exposes the underlying sampler via `f.__sampler__` for
inspection or testing.

## Bucketing

Entries are bucketed by `(source, level)`.  A `None` source is treated as an
empty string so it forms its own bucket rather than raising an error.

## Caveats

- The sampler is **stateful** — create a new instance (or call `reset()`) when
  you start tailing a new file to avoid stale counters.
- Sampling is deterministic (counter-based), not random, so the *first* entry
  in each bucket is always forwarded.
