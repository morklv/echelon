from fastapi import WebSocket
import json

connected_clients: list[WebSocket] = []
# stores all currently connected dashboard websocket clients

recent_events = set()
# prevents repeated spam notifications


async def connect_client(websocket: WebSocket):
    # runs when browser connects to /ws

    await websocket.accept()

    connected_clients.append(websocket)


async def disconnect_client(websocket: WebSocket):
    # runs when browser disconnects

    if websocket in connected_clients:
        connected_clients.remove(websocket)


async def broadcast_event(event_data: dict):
    # sends structured event information
    # to all connected dashboards

    event_key = json.dumps(
        event_data,
        sort_keys=True
    )

    # prevents duplicate spam events
    if event_key in recent_events:
        return

    recent_events.add(event_key)

    # clears memory periodically
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

    # removes dead websocket connections
    for client in disconnected_clients:
        if client in connected_clients:
            connected_clients.remove(client)