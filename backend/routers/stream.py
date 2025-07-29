from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .shared_instances import muselsl_stream_service

stream_router = APIRouter()

@stream_router.get("/start-muselsl-stream")
def start_stream(mac_address: str):
    return muselsl_stream_service.start_muselsl_stream(mac_address)

@stream_router.get("/end-stream")
def end_stream():
    return muselsl_stream_service.end_stream()


