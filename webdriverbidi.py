import json
import logging
from typing import Optional

from websockets.sync import client


def _make_command(method: str, params: Optional[dict] = None) -> dict:
    return {
        "id": 1,
        "method": method,
        "params": params or {},
    }


def _send_command(
    ws: client.ClientConnection, method: str, params: Optional[dict] = None
) -> Optional[dict]:
    ws.send(json.dumps(_make_command(method, params)))
    if response := ws.recv():
        data = json.loads(response)
        if data.get("type") == "success":
            return data["result"]
        if data.get("type") == "error":
            logging.error(f"Error: {data['error']}, Message: {data['message']}")
    return None


class Session:
    def __init__(self, ws: client.ClientConnection) -> None:
        self.ws = ws

    def _new(self) -> Optional[str]:
        if response := _send_command(
            self.ws,
            "session.new",
            {"capabilities": {}},
        ):
            return response["sessionId"]
        return None

    def _end(self) -> bool:
        return _send_command(self.ws, "session.end", {}) is not None

    def __enter__(self) -> "Session":
        assert self._new()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        assert self._end()

    def __call__(self, method: str, params: Optional[dict] = None) -> Optional[dict]:
        return _send_command(self.ws, method, params)


def execute(port: int, method: str, params: Optional[dict] = None) -> Optional[dict]:
    with client.connect(f"ws://localhost:{port}/session") as websocket:
        with Session(websocket) as session:
            return session(method, params)
    return None
