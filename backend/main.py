from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from muselslStream import get_devices_list

app = FastAPI()

# Allow requests from your frontend (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}


@app.get("/api/devices")
def read_root():
    response = get_devices_list()
    print(response)
    return {"message": response}