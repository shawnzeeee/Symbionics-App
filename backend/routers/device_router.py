from fastapi import APIRouter
from services.device_service import DeviceService

device_router = APIRouter()
device_service = DeviceService()

@device_router.get("/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}

@device_router.get("/devices")
def get_devices():
    devices = device_service.get_devices()
    return {"data": devices}
