import json
import os
import socket
import struct
from pathlib import Path

import requests

task_path = Path(__file__).parent.parent

MC_ADDRESS = "dratewka-simulator.hack4krak.pl" if os.getenv("TASKS_TARGET") == "prod" else "localhost"
SERVICE_PORT = 25565
PACK_URL = "https://cdn.modrinth.com/data/K4CZat30/versions/OmbYrI4q/respack.zip"


def ping_mc_server(ip, port=25565):
    """Ping a Minecraft server and return server info"""

    def read_var_int(sock):
        i = 0
        j = 0
        while True:
            k = sock.recv(1)
            if not k:
                return 0
            k = k[0]
            i |= (k & 0x7F) << (j * 7)
            j += 1
            if j > 5:
                raise ValueError("var_int too big")
            if not (k & 0x80):
                return i

    sock = socket.create_connection((ip, port), timeout=5)
    sock.settimeout(5)
    try:
        host = ip.encode("utf-8")
        data = b""  # wiki.vg/Server_List_Ping
        data += b"\x00"  # packet ID
        data += b"\x04"  # protocol variant
        data += struct.pack(">b", len(host)) + host
        data += struct.pack(">H", port)
        data += b"\x01"  # next state
        data = struct.pack(">b", len(data)) + data
        sock.sendall(data + b"\x01\x00")  # handshake + status ping
        length = read_var_int(sock)  # full packet length
        if length < 10:
            if length < 0:
                raise ValueError("negative length read")
            else:
                raise ValueError(f"invalid response {sock.recv(length)}")

        sock.recv(1)  # packet type, 0 for pings
        length = read_var_int(sock)  # string length
        data = b""
        while len(data) != length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                raise ValueError("connection aborted")
            data += chunk

        return json.loads(data)
    finally:
        sock.close()


def test_server_alive():
    # Ping the Minecraft server to check if it's alive
    server_data = ping_mc_server(MC_ADDRESS, SERVICE_PORT)
    # Basic validation that we got a proper response
    assert "version" in server_data
    assert "players" in server_data
    assert "description" in server_data


def test_pack_url_downloadable():
    response = requests.get(PACK_URL, timeout=5)
    assert response.status_code == 200
    # Check that we got some content (file download)
    assert len(response.content) > 0
