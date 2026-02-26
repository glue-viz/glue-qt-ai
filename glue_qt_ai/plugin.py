"""
Glue plugin registration for AI Bridge.
"""

from qtpy.QtWidgets import QMessageBox
from glue_qt.config import menubar_plugin


def toggle_bridge(session, data_collection):
    """Toggle the AI bridge server on/off."""
    from glue_qt_ai.server import start_bridge_server, stop_bridge_server

    app = session.application

    if hasattr(app, '_ai_bridge_server') and app._ai_bridge_server is not None:
        # Bridge is running - offer to stop it
        msg = QMessageBox(app)
        msg.setWindowTitle("AI Bridge")
        msg.setText("AI bridge server is currently running.")
        msg.setInformativeText(
            f"Listening on port {app._ai_bridge_server.port}.\n\n"
            "Do you want to stop it?"
        )
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            stop_bridge_server(app)
            QMessageBox.information(app, "AI Bridge", "Bridge server stopped.")
    else:
        # Bridge is not running - start it
        server = start_bridge_server(app)
        if server:
            QMessageBox.information(
                app,
                "AI Bridge",
                f"Bridge server started on port {server.port}.\n\n"
                "You will be prompted to approve each new connection."
            )
        else:
            QMessageBox.critical(
                app,
                "AI Bridge",
                "Failed to start bridge server."
            )


def setup_plugin():
    """Register the plugin with glue."""
    menubar_plugin.add("AI Bridge...", toggle_bridge)
