from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.device_router import device_router
from routers.stream_router import stream_router
from routers.calibration_router import calibration_router
from routers.loadCsvFiles import router as file_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device_router, prefix="/api")
app.include_router(stream_router, prefix="/api")
app.include_router(calibration_router, prefix="/api")
app.include_router(file_router, prefix="/api")
