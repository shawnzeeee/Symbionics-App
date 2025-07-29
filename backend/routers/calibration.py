from fastapi import APIRouter, WebSocket
from .shared_instances import calibration_service


calibration_router = APIRouter()

@calibration_router.get("/begin-calibration")
def begin_calibration(file_name: str):
    return calibration_service.begin_calibration()

@calibration_router.websocket("/signal-quality")
async def check_signal(websocket: WebSocket):
    await websocket.accept()
    file_name = websocket.query_params.get("file_name")
    await calibration_service.begin_checking_signal(websocket, file_name)
    await websocket.close()

@calibration_router.get("/end-stream")
def end_stream():
    return calibration_service.disconnect_muse()