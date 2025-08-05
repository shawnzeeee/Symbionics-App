import os
import shutil
from pathlib import Path

def LoadCsvToPi(filename):
    relative_path = Path(__file__).resolve().parent.parent / "SavedData"
    source_file = relative_path / filename  # Replace with your file path
    usb_drive_letter = "D"  # Replace with your USB drive letter
    # target_filename = "test2.csv"  # Optional rename on USB

    # === Build the target path ===
    usb_mount_path = f"{usb_drive_letter}:/"
    target_path = os.path.join(usb_mount_path, "calibration.csv")

    # === Check if USB drive exists ===
    if not os.path.exists(usb_mount_path):
        print(f"USB drive '{usb_mount_path}' not found. Please insert the USB drive and try again.")
        return ("im boutta buss with no usb found")

    # === Check if source file exists ===
    if not os.path.isfile(source_file):
        print(f"Source file '{source_file}' does not exist.")
        return ("im boutta buss with no source file found")

    # === Copy the file ===
    try:
        # Just copy — let it overwrite if allowed
        shutil.copyfile(source_file, target_path)
        return f"Copied '{filename}' to '{target_path}'"

    except PermissionError as e:
        raise PermissionError(f"Permission denied: {e}")
    except Exception as e:
        raise IOError(f"Failed to copy file: {e}")