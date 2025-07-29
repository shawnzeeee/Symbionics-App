from fastapi import APIRouter
from services.calibration_service import CalibrationService

calibration_router = APIRouter()
calibration_service = CalibrationService()

@calibration_router.get("/begin-calibration")
def begin_calibration(file_name: str):
    return calibration_service.begin_calibration(file_name)
