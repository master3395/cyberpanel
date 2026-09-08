"""Read server public IP from /etc/cyberpanel/machineIP with safe fallbacks."""
import socket

MACHINE_IP_FILE = '/etc/cyberpanel/machineIP'
DEFAULT_IP = '127.0.0.1'


def read_machine_ip(default=None):
    """
    Return the CyberPanel machine IP.

    Prefer /etc/cyberpanel/machineIP. Do not call ACLManager.GetServerIP here —
    that helper imports this function and would recurse.
    """
    if default is None:
        default = DEFAULT_IP
    try:
        with open(MACHINE_IP_FILE, 'r', encoding='utf-8', errors='replace') as handle:
            line = handle.read().split('\n', 1)[0].strip()
            if line:
                return line
    except OSError:
        pass
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return default
