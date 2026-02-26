"""
Glue plugin registration for AI Bridge.
"""

from qtpy.QtWidgets import QMessageBox, QInputDialog
from glue_qt.config import menubar_plugin


def toggle_bridge(session, data_collection):
    """Toggle the AI bridge server on/off."""
    from glue_qt_ai.server import start_bridge_server, stop_bridge_server, DEFAULT_PORT

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
        # Bridge is not running - offer to start it
        port, ok = QInputDialog.getInt(
            app,
            "AI Bridge",
            "Enter port number for bridge server:",
            DEFAULT_PORT,
            1024,
            65535
        )

        if ok:
            server = start_bridge_server(app, port=port)
            if server:
                QMessageBox.information(
                    app,
                    "AI Bridge",
                    f"Bridge server started on port {port}.\n\n"
                    "You will be prompted to approve each new connection."
                )
            else:
                QMessageBox.critical(
                    app,
                    "AI Bridge",
                    f"Failed to start bridge server on port {port}.\n"
                    "The port may already be in use."
                )


def setup_plugin():
    """Register the plugin with glue."""
    menubar_plugin.add("AI Bridge...", toggle_bridge)
