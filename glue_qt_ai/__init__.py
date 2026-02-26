"""
Glue-Qt AI Bridge

A plugin that enables AI assistants (like Claude Code) to control glue-qt
via a socket-based bridge.

Usage:
    1. Install: pip install glue-qt-ai
    2. Start glue: glue
    3. Enable bridge: Plugins → AI Bridge...
    4. Connect from AI assistant or script
"""

from glue_qt_ai.server import (
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
    from glue_qt_ai.plugin import setup_plugin
    setup_plugin()
