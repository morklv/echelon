from fastapi import WebSocket
import json

connected_clients: list[WebSocket] = []
recent_events = set()

async def connect_client(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)


async def disconnect_client(websocket: WebSocket):
    if websocket in connected_clients:
        connected_clients.remove(websocket)


async def broadcast_event(event_data: dict):
    event_key = json.dumps(
        event_data,
        sort_keys=True
    )

    if event_key in recent_events:
        return

    recent_events.add(event_key)

    if len(recent_events) > 50:
        recent_events.clear()

    disconnected_clients = []

    for client in connected_clients:
        try:
            await client.send_text(
                json.dumps(event_data)
            )

        except Exception:
            disconnected_clients.append(client)

    for client in disconnected_clients:
        if client in connected_clients:
            connected_clients.remove(client)