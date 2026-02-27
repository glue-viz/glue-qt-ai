# glue-qt-llm-bridge

A plugin for [glue-qt](https://github.com/glue-viz/glue-qt) that enables AI assistants (like Claude Code) to programmatically control glue.

**This package is experimental!**

## Installation

```bash
pip install git+https://github.com/glue-viz/glue-qt-llm-bridge
```

## Usage

1. Start glue: `glue`
2. Go to **Plugins → AI Bridge...**
3. Tell your AI assistant about the bridge, e.g.:

```
The glue-qt-llm-bridge package is installed. Check `glue_qt_llm_bridge.__doc__` for instructions on how to connect to and control glue.
```

Or in a CLAUDE.md / system prompt:

```
To control glue-qt, run: python -c "import glue_qt_llm_bridge; print(glue_qt_llm_bridge.__doc__)"
```

4. Tell your AI assistant what you want to do in glue, for example:

_Please load data from <directory> and make a scatter plot of temperature versus time.
_

## License

BSD 3-Clause License
