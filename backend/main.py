from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from muselslStream import get_devices_list
import re

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
    lines = response.strip().splitlines()
    devices = []
    print(response)
    for line in lines[1:]:
        if line == "No Muses found":
            break
        if "Found device" in line and "MAC Address" in line:
            match = re.search(r"Found device (Muse-\w+), MAC Address ([\dA-F:]+)", line)     
            device = {
                "name": match.group(1),
                "mac": match.group(2)
            }  
            devices.append(device)
            
    print(devices)
    return {"message": devices}