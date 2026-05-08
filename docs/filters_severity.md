# Severity Burst Filter

The **severity burst filter** dynamically adjusts the minimum visible log level
based on recent activity.  During quiet periods only high-priority entries are
forwarded; when a burst of critical entries is detected the filter relaxes and
lets everything through.

## Motivation

Game engines are noisy.  During normal play you rarely care about `DEBUG` or
`INFO` messages, but when something goes wrong you want the full picture.
The severity burst filter gives you that automatically — no manual toggling
required.

## API

```python
from gamelog_tail.filters_severity import severity_burst_filter

f = severity_burst_filter(
    quiet_min_level="warning",    # block below this level when quiet
    burst_trigger_level="error",  # entries at this level or above count toward burst
    burst_threshold=3,            # how many trigger entries within the window start a burst
    window_seconds=10.0,          # rolling time window in seconds
)
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `quiet_min_level` | `"warning"` | Minimum level passed when **not** in a burst |
| `burst_trigger_level` | `"error"` | Level that increments the burst counter |
| `burst_threshold` | `3` | Number of trigger entries needed to activate burst mode |
| `window_seconds` | `10.0` | Rolling window for counting trigger entries |

### Level names

Accepted values (case-insensitive): `debug`, `info`, `warning`, `error`, `fatal`.

## Example

```python
from gamelog_tail.filters_severity import severity_burst_filter
from gamelog_tail.pipeline import run

filters = [severity_burst_filter(burst_threshold=2, window_seconds=5)]
run(parser, filters, formatter, stream)
```

During normal play only `warning` and above are shown.  As soon as two `error`
entries appear within five seconds, the filter opens up and all levels pass
until the burst window expires.
