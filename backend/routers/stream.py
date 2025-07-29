from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.muselsl_stream_service import MuselslStreamService

stream_router = APIRouter()
stream_service = MuselslStreamService()

@stream_router.get("/start-muselsl-stream")
def start_stream(mac_address: str):
    return stream_service.start_stream(mac_address)

@stream_router.get("/end-stream")
def end_stream():
    return stream_service.end_stream()

@stream_router.websocket("/check-signal")
async def check_signal(websocket: WebSocket):
    await stream_service.check_signal(websocket)
