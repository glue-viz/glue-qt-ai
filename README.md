# glue-qt-ai

A plugin for [glue-qt](https://github.com/glue-viz/glue-qt) that enables AI assistants (like Claude Code) to programmatically control glue.

**This package is experimental!**

## Installation

```bash
pip install git+https://github.com/glue-viz/glue-qt-ai
```

## Usage

1. Start glue: `glue`
2. Go to **Plugins → AI Bridge...**
3. Tell your AI assistant about the bridge, e.g.:

```
The glue-qt-ai package is installed. Check `glue_qt_ai.__doc__` for instructions on how to connect to and control glue.
```

Or in a CLAUDE.md / system prompt:

```
To control glue-qt, run: python -c "import glue_qt_ai; print(glue_qt_ai.__doc__)"
```

4. Tell your AI assistant what you want to do in glue, for example:

```
Please load data from <directory> and make a scatter plot of temperature versus time.
```

## License

BSD 3-Clause License
