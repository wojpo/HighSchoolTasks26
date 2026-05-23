import os
import socket
import subprocess
from pathlib import Path

task_path = Path(__file__).parent.parent

HOST = "krakow-arcade-museum.hack4krak.pl" if os.getenv("TASKS_TARGET") == "prod" else "127.0.0.1"
PORT = 2222
KNOWN_HOSTS = Path(os.getenv("PYTEST_TMPDIR", "/tmp")) / "krakow-arcade-museum-known-hosts"
SSH_COMMAND = [
    "ssh",
    "-tt",
    "-o",
    "BatchMode=yes",
    "-o",
    "PreferredAuthentications=none,password",
    "-o",
    "PubkeyAuthentication=no",
    "-o",
    "StrictHostKeyChecking=accept-new",
    "-p",
    str(PORT),
    "-o",
    f"UserKnownHostsFile={KNOWN_HOSTS}",
    f"player@{HOST}",
]


def _timeout_output(exception: subprocess.TimeoutExpired) -> str:
    stdout = exception.stdout
    stderr = exception.stderr
    if isinstance(stdout, bytes):
        stdout = stdout.decode(errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode(errors="replace")
    return (stdout or "") + (stderr or "")


def test_ssh_port_open():
    sock = socket.create_connection((HOST, PORT), timeout=5)
    try:
        banner = sock.recv(1024)
        assert banner.startswith(b"SSH-"), f"Expected SSH banner, got: {banner[:50]}"
    finally:
        sock.close()


def test_ssh_login_starts_game():
    try:
        proc = subprocess.run(
            SSH_COMMAND,
            input="q",
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        output = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as exception:
        output = _timeout_output(exception)

    assert "KRAKOW ARCADE MUSEUM" in output, output
    assert "WASD ruch" in output, output
    assert "Connection closed by remote host" not in output, output
