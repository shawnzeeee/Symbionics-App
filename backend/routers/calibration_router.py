from fastapi import APIRouter, WebSocket
from .shared_instances import calibration_service
# routers/calibration_router.py
import asyncio, contextlib, json
from fastapi import WebSocket, WebSocketDisconnect

calibration_router = APIRouter()

@calibration_router.get("/update-csv")
def updateCSV(filename: str, adder: int, subtractor: int):
    return calibration_service.updateCSV(filename, adder, subtractor)

@calibration_router.get("/begin-pylsl-stream")
def begin_pylsl_stream(file_name: str):
    return calibration_service.begin_pylsl_stream(file_name)

@calibration_router.get("/begin-pylsl-stream-no-file-write")
def begin_pylsl_stream_no_file_write(file_name: str):
    return calibration_service.begin_pylsl_stream_no_file_write(file_name)

@calibration_router.get("/end-muse-pylsl-stream")
def end_muse_pylsl_stream():
    return calibration_service.end_muse_pylsl_stream()

@calibration_router.get("/begin-calibration")
def begin_calibration():
    return calibration_service.begin_calibration()

@calibration_router.websocket("/signal-quality")
async def check_signal(websocket: WebSocket):
    await websocket.accept()
    await calibration_service.begin_checking_signal(websocket)
    await websocket.close()

@calibration_router.get("/train-svm")
async def train_svm(file_name: str):
    print("training SVM backend function with csv:")
    print(file_name)
    return calibration_service.train_classifier(file_name)

@calibration_router.websocket("/attention-threshold")
async def attention_threshold(websocket: WebSocket):
    await websocket.accept()
    # await calibration_service.begin_checking_attention_threshold(websocket)
    # await websocket.close()

    async def reader():
        try:
            while True:
                msg = await websocket.receive_text()
                try:
                    data = json.loads(msg)
                except Exception:
                    continue

                if "attention_adder" in data or "attention_subtractor" in data:
                    await calibration_service.set_attention_adjustments(
                        data.get("attention_adder"),
                        data.get("attention_subtractor"),
                    )
                    a, s = await calibration_service.get_attention_adjustments()
                    # optional ack so UI can reflect clamping
                    await websocket.send_json({
                        "type": "ack",
                        "attention_adder": a,
                        "attention_subtractor": s,
                    })
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print("WS reader error:", e)

    reader_task = asyncio.create_task(reader())
    try:
        # your existing long-running sender loop (see step 3)
        await calibration_service.begin_checking_attention_threshold(websocket)
    finally:
        reader_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await reader_task
        with contextlib.suppress(Exception):
            await websocket.close()


@calibration_router.get("/end-stream")
def end_stream():
    return calibration_service.disconnect_muse()