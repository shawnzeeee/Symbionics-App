import threading
from calibration import calibrate
def main():
    record_data_event = threading.Event()
    record_data_event.clear()
    calibrate(record_data_event)

if __name__ == '__main__':
    main()