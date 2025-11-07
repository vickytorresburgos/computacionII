import struct
import json
import asyncio
from typing import Dict, Any

HEADER_SIZE = 8

def send_message(conn, data: Dict[str, Any]) -> None:
    """Envía un mensaje JSON con prefijo binario (bloqueante)."""
    encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
    header = struct.pack(">Q", len(encoded))
    conn.sendall(header + encoded)


def recv_all(conn, n: int) -> bytes:
    """Lee exactamente n bytes de un socket bloqueante."""
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Conexión cerrada prematuramente.")
        buf += chunk
    return buf


def recv_message(conn) -> Dict[str, Any]:
    """Recibe un mensaje binario y lo decodifica (bloqueante)."""
    header = recv_all(conn, HEADER_SIZE)
    length = struct.unpack(">Q", header)[0]
    body = recv_all(conn, length)
    return json.loads(body.decode("utf-8"))


async def send_message_async(writer: asyncio.StreamWriter, data: Dict[str, Any]) -> None:
    """Envía un mensaje JSON asíncrono con prefijo binario."""
    encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
    header = struct.pack(">Q", len(encoded))
    writer.write(header + encoded)
    await writer.drain()


async def recv_message_async(reader: asyncio.StreamReader) -> Dict[str, Any]:
    """Recibe un mensaje JSON asíncrono con prefijo binario."""
    header = await reader.readexactly(HEADER_SIZE)
    length = struct.unpack(">Q", header)[0]
    body = await reader.readexactly(length)
    return json.loads(body.decode("utf-8"))