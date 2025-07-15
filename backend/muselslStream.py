import time
from pylsl import StreamInlet, resolve_streams
import subprocess


def get_devices_list():
    print("[INFO] Getting available Muse Devices.")
    response = subprocess.run(['muselsl', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if response.stderr:
        return response.stderr
    else:
        return response.stdout
def start_muse_stream(MAC_ADDRESS):
    print("[INFO] Starting Muse stream...")
    # Start the stream in a background process
    return subprocess.Popen(["muselsl", "stream",'--address', MAC_ADDRESS], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def muse_connected():
    streams = resolve_streams()
    for stream in streams:
        if stream.type() == 'EEG' and 'Muse' in stream.name():
            print(f"[CONNECTED] Found stream: {stream.name()}")
            return True
    print("[NOT CONNECTED] No Muse EEG stream found.")
    return False

def wait_for_stream(timeout=10):
    print("[INFO] Waiting for EEG stream...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if muse_connected():
            return True
        time.sleep(1)
    raise TimeoutError("[ERROR] Timed out waiting for Muse EEG stream.")

def connect_to_eeg_stream():
    print("[INFO] Looking for an EEG stream...")
    streams = resolve_streams()
    if not streams:
        raise RuntimeError("[ERROR] No EEG stream found. Is Muse powered on?")
    print("[INFO] EEG stream found.")
    return StreamInlet(streams[0])


