import threading
from calibration import calibrate
from pathlib import Path
def main():
    # record_data_event = threading.Event()
    # record_data_event.clear()
    # calibrate(record_data_event)
    # Relative to the current file
    data_dir = Path(__file__).parent / "SavedData"
    file_path = data_dir / "shawn1"
    print(file_path)

if __name__ == '__main__':
    main()

