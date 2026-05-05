# gamelog-tail

Real-time log parser and filter for common game engine output formats.

---

## Installation

```bash
pip install gamelog-tail
```

Or install from source:

```bash
git clone https://github.com/yourname/gamelog-tail.git && cd gamelog-tail && pip install .
```

---

## Usage

Tail and filter a Unity or Unreal Engine log in real time:

```bash
# Follow a log file and show only warnings and errors
gamelog-tail --file ~/game/output.log --level warn

# Filter by keyword and highlight errors
gamelog-tail --file ~/game/output.log --grep "Player" --highlight error

# Pipe output from a running process
./MyGame | gamelog-tail --format unreal
```

**Supported engines / formats:**
- Unity (Player.log)
- Unreal Engine 4/5
- Godot
- Generic timestamped log output

**Available flags:**

| Flag | Description |
|------|-------------|
| `--file` | Path to log file |
| `--format` | Engine format (`unity`, `unreal`, `godot`, `generic`) |
| `--level` | Minimum log level to display (`debug`, `info`, `warn`, `error`) |
| `--grep` | Filter lines by keyword |
| `--highlight` | Colorize lines matching a keyword |

---

## Requirements

- Python 3.8+
- No external dependencies

---

## License

MIT © 2024 yourname