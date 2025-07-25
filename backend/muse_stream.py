import time
from pylsl import StreamInlet, resolve_streams
import subprocess
import numpy as np
from muse_validation import checkSignal
from muselsl.stream import stream
from muselsl.stream import list_muses
import threading

stream_process = None

import asyncio
def get_devices_list():
    print("[INFO] Getting available Muse Devices.")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        muses = list_muses()
        return muses
    finally:
        asyncio.set_event_loop(None)
    
    
def start_muse_stream(MAC_ADDRESS, start_event, stop_event):
    print("[INFO] Starting muselsl stream...")
    global stream_process
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stream(MAC_ADDRESS, start_event, stop_event)
        print("Connected")
    finally:
        asyncio.set_event_loop(None)
    
def end_muse_stream():
    print("[INFO] Ending muselsl stream...")
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
            print(f"[CONNECTED] pylsl found stream: {stream.name()}")
            return True
    return False

def wait_for_stream(timeout=10):
    print("[INFO] pylsl waiting for EEG stream...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if muse_connected():
            return True
        time.sleep(1)
    raise TimeoutError("[ERROR] Timed out waiting for Muse EEG stream.")

def connect_to_eeg_stream():
    streams = resolve_streams()
    if not streams:
        raise RuntimeError("[ERROR] pylsl could not find EEG stream. Is Muse powered on?")
    print("[INFO] pylsl found muselsl EEG stream.")
    return StreamInlet(streams[0])

eeg_buffer = None
eeg_buffer_lock = threading.Lock()

def update_eeg_buffer(stop_event):
    global eeg_buffer
    buffer_size = 4 * 250 *2
    eeg_buffer = np.zeros(buffer_size, dtype=np.float32)
    try:
        wait_for_stream(timeout=10)
        inlet = connect_to_eeg_stream()
        while not stop_event.is_set():
            sample, timestamp = inlet.pull_sample()
            with eeg_buffer_lock:
                eeg_buffer = np.roll(eeg_buffer, -4)      # Shift left by 4
                eeg_buffer[-4:] = sample[:4]              # Insert new sample at the end (right)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")
    except:
        print("\n Something went wrong creating EEG buffer")
    return "Stream Ended"


def check_signal(eeg_buffer):
    # eeg_buffer shape: (num_samples, num_channels)
    eeg_buffer = eeg_buffer.reshape(500,4)
    signal_quality = []
    for i in range(eeg_buffer.shape[1]):
        channel_data = eeg_buffer[:, i]
        std = channel_data.std()
        signal_quality.append(std)
    return {"TP9": signal_quality[0], "AF7": signal_quality[1], "AF8": signal_quality[2], "TP10": signal_quality[3]}

def get_eeg_buffer():
    global eeg_buffer
    return eeg_buffer

def main():
    muses = list_muses()
    print(muses)


if __name__ == "__main__":
    main()



