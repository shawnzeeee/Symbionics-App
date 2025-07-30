from fastapi import APIRouter, WebSocket
from .shared_instances import calibration_service


calibration_router = APIRouter()

@calibration_router.get("/begin-pylsl-stream")
def begin_pylsl_stream(file_name: str):
    return calibration_service.begin_pylsl_stream(file_name)

@calibration_router.get("/begin-calibration")
def begin_calibration():
    return calibration_service.begin_calibration()

@calibration_router.websocket("/signal-quality")
async def check_signal(websocket: WebSocket):
    await websocket.accept()
    await calibration_service.begin_checking_signal(websocket)
    await websocket.close()

@calibration_router.get("/end-stream")
def end_stream():
    return calibration_service.disconnect_muse()