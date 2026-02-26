# glue-qt-ai

A plugin for [glue-qt](https://github.com/glue-viz/glue-qt) that enables AI assistants (like Claude Code) to programmatically control glue via a socket-based bridge.

## Installation

```bash
pip install glue-qt-ai
```

Or for development:

```bash
git clone https://github.com/glue-viz/glue-qt-ai
cd glue-qt-ai
pip install -e .
```

## Quick Start

### 1. Start the bridge in glue

1. Start glue: `glue`
2. Go to **Plugins → AI Bridge...**
3. Enter port (default: 9876) and click OK

### 2. Send commands

```bash
python -m glue_qt_ai.client "print('Hello from glue!')"
python -m glue_qt_ai.client --eval "len(dc)"
```

### 3. Interactive mode

```bash
python -m glue_qt_ai.client -i
```

## Protocol

The bridge uses a simple JSON-over-TCP protocol on localhost.

### Connection Flow

1. Connect to `localhost:9876` (or configured port)
2. Wait for approval response (user sees a popup in glue)
3. If approved: `{"success": true, "message": "Connection approved"}`
4. If rejected: `{"success": false, "error": "Connection rejected by user"}`

### Command Format

Send JSON followed by newline:

```json
{"type": "exec", "code": "print('hello')"}
```

Or to evaluate an expression:

```json
{"type": "eval", "code": "len(dc)"}
```

### Response Format

```json
{
  "success": true,
  "result": "5",
  "stdout": "printed output\n",
  "stderr": ""
}
```

## Available Variables

Commands execute with these pre-defined variables:

| Variable | Description |
|----------|-------------|
| `app` / `application` | The GlueApplication instance |
| `dc` / `data_collection` | The DataCollection containing all datasets |
| `session` | The Session object |
| `hub` | The message Hub |
| `np` | NumPy (pre-imported) |
| `Data` | glue.core.Data class |

## Example Commands

### Load data
```python
app.load_data('/path/to/file.fits')
```

### Create a scatter plot
```python
from glue_qt.viewers.scatter import ScatterViewer
viewer = app.new_data_viewer(ScatterViewer, data=dc[0])
```

### Create a selection
```python
from glue.core.subset import InequalitySubsetState
import operator
state = InequalitySubsetState(dc[0].id['x'], 0.5, operator=operator.gt)
dc.new_subset_group('x > 0.5', state)
```

## Python Client Example

```python
from glue_qt_ai.client import send_command

# Execute code
result = send_command("app.load_data('data.fits')")

# Evaluate expression
result = send_command("len(dc)", cmd_type='eval')
print(result['result'])
```

## Security

- Server only listens on localhost (127.0.0.1)
- Each new connection requires user approval via popup dialog
- Once approved, a connection stays approved for the session

## For AI Assistants

If you're an AI assistant wanting to control glue:

1. Check if bridge is running: try connecting to localhost:9876
2. If connection refused, ask user to enable via Plugins → AI Bridge...
3. Wait for user to approve the connection (they'll see a popup)
4. Send Python commands as JSON: `{"type": "exec", "code": "..."}`
5. Parse JSON response to check success and get results
6. Use `dc`, `app`, `session` variables to interact with glue

## License

BSD 3-Clause License
