from fastapi import APIRouter, WebSocket
from .shared_instances import calibration_service


calibration_router = APIRouter()

@calibration_router.get("/begin-calibration")
def begin_calibration(file_name: str):
    return calibration_service.begin_calibration()

@calibration_router.websocket("/signal-quality")
async def check_signal(websocket: WebSocket):
    await calibration_service.begin_checking_signal(websocket)