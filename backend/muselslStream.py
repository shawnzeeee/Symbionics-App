import time
from pylsl import StreamInlet, resolve_streams
import subprocess
import numpy as np
from museValidation import checkSignal


eeg_buffer = None

stream_process = None

def get_devices_list():
    print("[INFO] Getting available Muse Devices.")
    response = subprocess.run(['muselsl', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if response.stderr:
        return response.stderr
    else:
        return response.stdout
    
    
def start_muse_stream(MAC_ADDRESS):
    print("[INFO] Starting Muse stream...")
    global stream_process
    response = subprocess.Popen(["muselsl", "stream",'--address', MAC_ADDRESS], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stream_process = response
    if response.stderr:
        return response.stderr
    else:
        return response.stdout
    
def end_muse_stream():
    print("[INFO] Starting Muse stream...")
    global stream_process
    proc = stream_process
    if proc:
        proc.terminate()
        proc.wait()
        stream_process = None
        print(f"[INFO] Stopped Muse stream")
        return True
    print(f"[WARN] No running stream")
    return False

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

def update_eeg_buffer():
    global eeg_buffer
    buffer_size = 4 * 250 *2
    eeg_buffer = np.zeros(buffer_size, dtype=np.float32)
    try:
        wait_for_stream(timeout=10)
        inlet = connect_to_eeg_stream()
        while True:
            sample, timestamp = inlet.pull_sample()
            print(sample)
            eeg_buffer = np.roll(eeg_buffer, -4)      # Shift left by 4
            eeg_buffer[-4:] = sample[:4]              # Insert new sample at the end (right)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")


def get_eeg_buffer():
    global eeg_buffer
    return eeg_buffer

# def main():
#     buffer_size = 4 * 250 *2
#     eeg_buffer = np.zeros(buffer_size, dtype=np.float32)
#     try:
#         wait_for_stream(timeout=10)
#         inlet = connect_to_eeg_stream()
#         while True:
#             sample, timestamp = inlet.pull_sample()
#             print(sample)
#             eeg_buffer = np.roll(eeg_buffer, 4)      # Shift right by 4
#             eeg_buffer[:4] = sample[:4]              # Insert new sample at the start
#             checkSignal(eeg_buffer)

#     except KeyboardInterrupt:
#         print("\n[INFO] Stopping...")


# if __name__ == "__main__":
#     main()



