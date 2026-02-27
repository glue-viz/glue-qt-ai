"""
# Glue-Qt LLM Bridge - Instructions for LLMs

## Overview
This bridge allows you to programmatically control glue-qt (an astronomy/science
visualization tool) via a socket connection.

## Connecting

1. **Check if bridge is available**: Try connecting to `localhost:9876`
2. **If connection refused**: Ask the user to enable the bridge via
   **Plugins → AI Bridge...** in glue
3. **Wait for approval**: User will see a popup to approve your connection
4. **Send commands**: Use JSON over TCP

## Protocol

### Send commands (newline-terminated JSON):
```json
{"type": "exec", "code": "print('hello')"}
{"type": "eval", "code": "len(dc)"}
```

### Response format:
```json
{"success": true, "result": "5", "stdout": "", "stderr": ""}
{"success": false, "error": "NameError...", "traceback": "..."}
```

## Command-line client
```bash
python -m glue_qt_llm_bridge.client "your_code_here"
python -m glue_qt_llm_bridge.client --eval "expression"
```

The client auto-detects the port from `~/.glue/bridge_port`.

## Session tokens (avoiding repeated approval dialogs)

The first connection requires manual user approval. Upon approval, the server
returns a session token. Pass this token to subsequent calls to skip the dialog:

```bash
# First call - user approves, token is printed
python -m glue_qt_llm_bridge.client "print('hello')"
# Output: GLUE_BRIDGE_TOKEN=<token>
#         hello

# Subsequent calls - use token for auto-approval
python -m glue_qt_llm_bridge.client --token <token> "print('world')"
```

The token is only valid for the current glue session and is never written to disk.

## Available Variables
- `app` - GlueApplication instance
- `dc` - DataCollection (list of datasets)
- `session` - Session object
- `hub` - Message hub
- `np` - NumPy

## Common Operations

### Load data
```python
app.load_data('/path/to/file.fits')
```

### Create dataset
```python
from glue.core import Data
data = Data(x=np.random.random(100), y=np.random.random(100), label='mydata')
dc.append(data)
```

### Create scatter plot
```python
from glue_qt.viewers.scatter import ScatterViewer
viewer = app.new_data_viewer(ScatterViewer, data=dc[0])
viewer.state.x_att = dc[0].id['x']
viewer.state.y_att = dc[0].id['y']
```

### Create histogram
```python
from glue_qt.viewers.histogram import HistogramViewer
viewer = app.new_data_viewer(HistogramViewer, data=dc[0])
viewer.state.x_att = dc[0].id['column_name']
```

### Create image viewer
```python
from glue_qt.viewers.image import ImageViewer
viewer = app.new_data_viewer(ImageViewer, data=dc[0])
```

### Make selection (subset)
```python
from glue.core.subset import InequalitySubsetState
import operator
state = InequalitySubsetState(dc[0].id['x'], 0.5, operator=operator.gt)
dc.new_subset_group('x > 0.5', state)
```

### Compare two columns
```python
state = InequalitySubsetState(dc[0].id['x'], dc[0].id['y'], operator=operator.gt)
dc.new_subset_group('x > y', state)
```

### Change colormap
```python
from matplotlib import cm
viewer.state.layers[0].cmap = cm.viridis
```

### Close viewers
```python
for tab in app.viewers:
    for v in tab[:]:
        v.close()
```

### Remove data
```python
dc.remove(dc[0])
```

### Get dataset info
```python
data = dc[0]
data.label          # name
data.shape          # dimensions
data.main_components  # list of columns
data['column']      # get column data as array
```

## Tips
- Always check `response['success']` before using results
- Use `--eval` for expressions that return values
- Datasets are accessed by index: `dc[0]`, `dc[1]`, etc.
- Components (columns) are accessed via `data.id['name']`
- Viewers are in `app.viewers[tab_index][viewer_index]`
"""

from glue_qt_llm_bridge.server import (
    GlueBridgeServer,
    start_bridge_server,
    stop_bridge_server,
    DEFAULT_PORT,
)

__version__ = "0.1.0"

__all__ = [
    'GlueBridgeServer',
    'start_bridge_server',
    'stop_bridge_server',
    'DEFAULT_PORT',
    'setup',
]


def setup():
    """Register the plugin with glue."""
    from glue_qt_llm_bridge.plugin import setup_plugin
    setup_plugin()
