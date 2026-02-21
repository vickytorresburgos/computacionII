import json
from typing import Any, Dict

def serialize_response(data: Dict[str, Any]) -> bytes:
    """Serializa una respuesta Python a bytes JSON UTF-8."""
    return json.dumps(data, ensure_ascii=False).encode("utf-8")

def deserialize_request(data: bytes) -> Dict[str, Any]:
    """Deserializa bytes JSON a un diccionario Python."""
    return json.loads(data.decode("utf-8"))