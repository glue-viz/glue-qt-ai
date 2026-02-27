"""
Glue-Qt AI Bridge Client

Simple client for sending commands to a running glue-qt bridge server.
"""

import json
import socket
import sys
from pathlib import Path

DEFAULT_HOST = 'localhost'
PORT_FILE = Path.home() / '.glue' / 'bridge_port'


def get_bridge_port():
    """Get the bridge port from the port file."""
    if PORT_FILE.exists():
        try:
            return int(PORT_FILE.read_text().strip())
        except (ValueError, IOError):
            pass
    raise ConnectionRefusedError(
        "Bridge port file not found. Is the bridge running? "
        "Enable it via Plugins → AI Bridge... in glue."
    )


class BridgeConnection:
    """Persistent connection to glue bridge server."""

    def __init__(self, host=DEFAULT_HOST, port=None, timeout=30, token=None):
        self.host = host
        self.port = port if port is not None else get_bridge_port()
        self.timeout = timeout
        self.token = token
        self.sock = None
        self.approved = False

    def connect(self):
        """Connect to the server and wait for approval."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

        # Send auth message with token (if we have one)
        auth_request = {'type': 'auth', 'token': self.token}
        self.sock.sendall((json.dumps(auth_request) + '\n').encode('utf-8'))

        # Wait for approval response
        response_data = self._receive_line()
        response = json.loads(response_data)

        if response.get('success'):
            self.approved = True
            # Capture token from server (for first-time approval)
            if response.get('token'):
                self.token = response['token']
            return True
        else:
            self.sock.close()
            self.sock = None
            raise ConnectionRefusedError(response.get('error', 'Connection rejected'))

    def send(self, code, cmd_type='exec'):
        """Send a command and receive response."""
        if not self.sock or not self.approved:
            raise ConnectionError("Not connected or not approved")

        request = {'type': cmd_type, 'code': code}
        request_json = json.dumps(request) + '\n'
        self.sock.sendall(request_json.encode('utf-8'))

        response_data = self._receive_line()
        return json.loads(response_data)

    def _receive_line(self):
        """Receive a single line response."""
        response_data = b''
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if b'\n' in response_data:
                break
        return response_data.decode('utf-8').strip()

    def close(self):
        """Close the connection."""
        if self.sock:
            self.sock.close()
            self.sock = None
            self.approved = False


# Global connection for reuse
_connection = None


def get_connection(host=DEFAULT_HOST, port=None, timeout=30, token=None):
    """Get or create a connection to the bridge server."""
    global _connection
    if _connection is None or _connection.sock is None:
        _connection = BridgeConnection(host, port, timeout, token)
        _connection.connect()
    return _connection


def send_command(code, cmd_type='exec', host=DEFAULT_HOST, port=None, timeout=30, token=None):
    """
    Send a command to the glue bridge server.

    Parameters
    ----------
    code : str
        Python code to execute or evaluate
    cmd_type : str
        'exec' for statements, 'eval' for expressions
    host : str
        Server host (default: localhost)
    port : int, optional
        Server port (default: auto-detect from port file)
    timeout : float
        Socket timeout in seconds
    token : str, optional
        Session token for auto-approval (obtained from first manual approval)

    Returns
    -------
    dict
        Response from server with keys: success, result, stdout, stderr, error, traceback
    """
    try:
        conn = get_connection(host, port, timeout, token)
        return conn.send(code, cmd_type)
    except (ConnectionError, BrokenPipeError, OSError):
        # Connection lost, clear it and retry once
        global _connection
        _connection = None
        conn = get_connection(host, port, timeout, token)
        return conn.send(code, cmd_type)


def glue_exec(code, **kwargs):
    """Execute Python statements in glue context."""
    result = send_command(code, cmd_type='exec', **kwargs)
    _print_result(result)
    return result


def glue_eval(code, **kwargs):
    """Evaluate Python expression in glue context and return result."""
    result = send_command(code, cmd_type='eval', **kwargs)
    _print_result(result)
    return result


def _print_result(result):
    """Print the result of a command."""
    if result.get('stdout'):
        print(result['stdout'], end='')
    if result.get('stderr'):
        print(result['stderr'], end='', file=sys.stderr)

    if result['success']:
        if result.get('result') is not None:
            print(result['result'])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        if result.get('traceback'):
            print(result['traceback'], file=sys.stderr)


def main():
    """Command-line interface."""
    import argparse
    parser = argparse.ArgumentParser(description='Send commands to glue AI bridge server')
    parser.add_argument('code', nargs='?', help='Python code to execute')
    parser.add_argument('--eval', '-e', action='store_true', help='Evaluate as expression')
    parser.add_argument('--host', default=DEFAULT_HOST, help='Server host')
    parser.add_argument('--port', type=int, default=None, help='Server port (default: auto-detect)')
    parser.add_argument('--token', '-t', default=None, help='Session token for auto-approval')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    args = parser.parse_args()

    if args.interactive:
        print("Glue AI Bridge Client - Interactive Mode")
        print("Type Python code to execute in glue. Prefix with '?' to evaluate.")
        print("Type 'quit' or 'exit' to quit.")
        print()

        # Connect and show token if this is first approval
        try:
            conn = get_connection(host=args.host, port=args.port, token=args.token)
            if conn.token and conn.token != args.token:
                print(f"Session token: {conn.token}")
                print("Use --token <token> for auto-approval in future connections.")
                print()
        except ConnectionRefusedError:
            print("Error: Could not connect to glue bridge server", file=sys.stderr)
            sys.exit(1)

        while True:
            try:
                code = input("glue> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not code:
                continue
            if code in ('quit', 'exit'):
                break

            cmd_type = 'exec'
            if code.startswith('?'):
                code = code[1:].strip()
                cmd_type = 'eval'

            try:
                result = send_command(code, cmd_type=cmd_type, host=args.host, port=args.port, token=args.token)
                _print_result(result)
            except ConnectionRefusedError:
                print("Error: Could not connect to glue bridge server", file=sys.stderr)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
    elif args.code:
        cmd_type = 'eval' if args.eval else 'exec'
        try:
            conn = get_connection(host=args.host, port=args.port, token=args.token)
            # Print token if this was first manual approval (token changed)
            if conn.token and conn.token != args.token:
                print(f"GLUE_BRIDGE_TOKEN={conn.token}")
            result = conn.send(args.code, cmd_type)
            _print_result(result)
            sys.exit(0 if result['success'] else 1)
        except ConnectionRefusedError:
            print("Error: Could not connect to glue bridge server", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
