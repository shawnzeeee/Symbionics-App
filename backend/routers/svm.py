# backend/routers/websocket.py
# from fastapi import APIRouter, WebSocket
# import asyncio

# router = APIRouter()

# @router.websocket("/ws/attention")
# async def attention_socket(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             await websocket.send_text("77")  # Simulated attention threshold
#             await asyncio.sleep(1)
#     except Exception as e:
#         print("WebSocket disconnected:", e)
