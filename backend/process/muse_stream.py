import time
from pylsl import StreamInlet, resolve_streams
import subprocess
import numpy as np
from muse_validation import check_signal
from muselsl.stream import stream
from muselsl.stream import list_muses
import threading
import mmap
import csv
from .calibration import get_gesture_code
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
sample = None
timestamp = None

classifcation = 0
classification_lock = threading.Lock()

def begin_streaming_data(file_path, start_event, stop_event, record_data_event):
    global eeg_buffer, sample, timestamp
    buffer_size = 4 * 250 *2
    eeg_buffer = np.zeros(buffer_size, dtype=np.float32)
    previous_class=0
    try:
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Classification"])
            wait_for_stream(timeout=10)
            inlet = connect_to_eeg_stream()
            start_event.set()
            while not stop_event.is_set():
                sample, timestamp = inlet.pull_sample()
                if record_data_event.is_set():
                    classification = get_gesture_code()
                    send_code = 0
                    if classification != previous_class:
                        send_code = classification
                    previous_class = classification
                    writer.writerow([sample[0], sample[1], sample[2], sample[3], send_code])
                #with eeg_buffer_lock:
                eeg_buffer = np.roll(eeg_buffer, -4)      # Shift left by 4
                eeg_buffer[-4:] = sample[:4]              # Insert new sample at the end (right)
            print("Ending pylsl_stream")
    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")
    except Exception as e:
        print(f"\n Something went wrong creating EEG buffer: {e}")

    print("Ending pylsl_stream")
    return "Stream Ended"

def save_data_to_csv():
    return


async def check_signal(websocket, stop_event):
    global eeg_buffer, eeg_buffer_lock
    try:
        while not stop_event.is_set():
            # Wait until eeg_buffer is ready and has enough data
            if eeg_buffer is None or eeg_buffer.size < 2000:
                await asyncio.sleep(0.1)
                continue
            input_buffer = eeg_buffer.reshape(500, 4)
            signal_quality = []
            for i in range(input_buffer.shape[1]):
                channel_data = input_buffer[:, i]
                std = channel_data.std()
                signal_quality.append(std)
            await websocket.send_json({
                "TP9": float(signal_quality[0]),
                "AF7": float(signal_quality[1]),
                "AF8": float(signal_quality[2]),
                "TP10": float(signal_quality[3])
            })
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f'There has been an error in check_signal: {e}')
    return

def get_eeg_buffer():
    global eeg_buffer
    return eeg_buffer

def main():
    muses = list_muses()
    print(muses)


if __name__ == "__main__":
    main()



