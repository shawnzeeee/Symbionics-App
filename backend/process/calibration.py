import cv2
import time
import random
import numpy as np
import os
import struct
import math
import mmap
import threading
script_dir = os.path.dirname(os.path.abspath(__file__))


# --- CONFIG ---
video_list = [ 
         os.path.join(script_dir,"../Videos/Handclose2.mp4"),
]

#for controlled randomness
play_counts = {path: 0 for path in video_list}

play_order = []

gesture_labels = {
   # "Handopen2.mp4": "Open Hand",
    "Handclose2.mp4": "Wait to Close Hand...",
}

cycle_duration = 8
break_duration = 8
total_duration = 60 * 2
# total_duration = 
cycle_count = 7
count = 0

exit_flag = False

gesture_code = 0
gesture_code_lock = threading.Lock()
# Put these near your other config values
PREROLL_S = 2.0     # freeze on first frame before instructions show
POST_HOLD_S = 6.0   # freeze on last frame after playback
#sound helpers
# --- Sound indicator helpers ---
_last_label_played = None

# Prefer winsound on Windows, fallback to simpleaudio elsewhere
try:
    import winsound
    _HAS_WINSOUND = True
except Exception:
    _HAS_WINSOUND = False

try:
    import simpleaudio as sa
    _HAS_SA = True
except Exception:
    _HAS_SA = False

def _play_tone(freq=700, ms=150, volume=0.5):
    """Play a short tone. Non-blocking on simpleaudio, blocking on winsound."""
    if _HAS_WINSOUND:
        winsound.Beep(int(freq), int(ms))
        return

    if _HAS_SA:
        import numpy as np
        fs = 44100
        t = np.linspace(0, ms/1000.0, int(fs*ms/1000.0), False)
        wave = (np.sin(2*np.pi*freq*t) * (32767*volume)).astype(np.int16)
        sa.play_buffer(wave, 1, 2, fs)  # non-blocking
        return
    # No audio backend available; silently skip

def announce_instruction(label: str):
    """
    Beep once whenever the instruction switches to OPEN HAND or CLOSE HAND.
    Use distinct tones so you can tell them apart by ear.
    """
    global _last_label_played
    if label not in ("OPEN HAND", "CLOSE HAND"):
        return
    if label == _last_label_played:
        return  # no change; avoid spamming

    freq = 700 if label == "OPEN HAND" else 900  # different pitch per instruction
    _play_tone(freq=freq, ms=160, volume=0.6)
    _last_label_played = label

# --- HELPER FUNCTIONS ---
def get_least_played_video():
    min_play = min(play_counts.values())
    candidates = [v for v in video_list if play_counts[v] == min_play]
    chosen = random.choice(candidates)
    play_counts[chosen] += 1
    return chosen

previous_class = 0
WINDOW_NAME = "Display"

def ensure_window_on_top(win=WINDOW_NAME):
    # Create once, make resizable, keep on top, and pump WM events
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(win, 1080, 1920)  # optional

    cv2.waitKey(1)  # give the WM a tick


def show_page_and_wait(page_img, win=WINDOW_NAME):
    cv2.imshow(win, page_img)
    # Re-assert topmost and pump events so it grabs focus
    cv2.setWindowProperty(win, cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(1)

    while True:
        k = cv2.waitKey(0) & 0xFF
        # Enter keys: handle both 13 (CR) and 10 (LF)
        if k in (13, 10, ord('\r'), ord('\n')):
            return "continue"
        # Optional: ESC or 'q' aborts
        if k in (27, ord('q')):
            return "quit"

def play_balanced_videos_for(_duration=None):
    """
    Play exactly ONE video (with all existing overlays handled inside
    play_video_then_countdown), then return so the break runs next.
    """
    video_path = get_least_played_video()
    gesture_index = video_list.index(video_path)

    # record what played and when (kept from your original behavior)
    timestamp = int(time.time() * 1000)  # ms
    play_order.append((video_path, timestamp))
    # print(f"[PLAY] {os.path.basename(video_path)} (index: {gesture_index + 1}) at {timestamp}")

    # Plays the clip once (first-frame freeze, red text, playback, last-frame hold)
    play_video_then_countdown(video_path, gesture_index)

    # Done after a single clip
    return

def play_video_then_countdown(path, gesture_index):
    """
    CLOSE phase:
    - Freeze on first frame (title only) for PREROLL_S
    - Show red 'Close your hand!' and play video
    - Freeze on final frame (same overlays) for POST_HOLD_S
    """
    global exit_flag

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"Cannot open: {path}")
        return

    # fps/delay
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1e-3:
        fps = 30.0
    delay_ms = int(1000.0 / fps)

    # window once
    cv2.namedWindow("Display", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Display", 720, 720)

    # read FIRST frame
    ret, frame = cap.read()
    if not ret:
        cap.release()
        print(f"Error: No frames in {path}")
        return
    first_frame = cv2.resize(frame, (720, 720))

    # title/label
    filename = os.path.basename(path)
    label = gesture_labels.get(filename, filename)  # e.g., "Wait to Close Hand..."

    # ---- 1) FREEZE on first frame (TITLE ONLY) ----
    t0 = time.time()
    while time.time() - t0 < PREROLL_S:
        overlay = first_frame.copy()

        # black title at top center
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(label, font, 1.2, 3)
        text_x = (overlay.shape[1] - text_size[0]) // 2
        cv2.putText(overlay, label, (text_x, 60), font, 1.2, (0, 0, 0), 3)

        # progress bar
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(overlay, progress)

        cv2.imshow("Display", overlay)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            exit_flag = True
            cap.release()
            return

    # At the moment red text appears, send class for CLOSE
    send_gesture_classification(2)

    # ---- 2) PLAYBACK with TITLE + RED TEXT ----
    last_frame = first_frame
    curr = frame
    keep_ret = ret
    while True:
        if keep_ret:
            img = curr
            keep_ret = False
        else:
            ret, img = cap.read()
            if not ret:
                break

        resized = cv2.resize(img, (720, 720))
        last_frame = resized.copy()

        # TITLE (black)
        font = cv2.FONT_HERSHEY_SIMPLEX
        tsize, _ = cv2.getTextSize(label, font, 1.2, 3)
        tx = (resized.shape[1] - tsize[0]) // 2
        cv2.putText(resized, label, (tx, 60), font, 1.2, (0, 0, 0), 3)

        # RED instruction
        red_text = "Close your hand!"
        rsize, _ = cv2.getTextSize(red_text, font, 1.5, 3)
        rx = (resized.shape[1] - rsize[0]) // 2
        cv2.putText(resized, red_text, (rx, 120), font, 1.5, (0, 0, 255), 3)
        #add sound input
        announce_instruction("CLOSE HAND")
        # progress
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(resized, progress)

        cv2.imshow("Display", resized)
        if cv2.waitKey(delay_ms) & 0xFF == ord('q'):
            exit_flag = True
            cap.release()
            return

    cap.release()

    # ---- 3) FREEZE on LAST frame (TITLE + RED TEXT) ----
    t1 = time.time()
    while time.time() - t1 < POST_HOLD_S:
        overlay = last_frame.copy()

        # TITLE
        font = cv2.FONT_HERSHEY_SIMPLEX
        tsize, _ = cv2.getTextSize(label, font, 1.2, 3)
        tx = (overlay.shape[1] - tsize[0]) // 2
        cv2.putText(overlay, label, (tx, 60), font, 1.2, (0, 0, 0), 3)

        # RED instruction
        red_text = "HOLD CLOSED!"
        rsize, _ = cv2.getTextSize(red_text, font, 1.5, 3)
        rx = (overlay.shape[1] - rsize[0]) // 2
        cv2.putText(overlay, red_text, (rx, 120), font, 1.5, (0, 0, 255), 3)

        # progress
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(overlay, progress)

        cv2.imshow("Display", overlay)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            exit_flag = True
            return

def show_break(duration):
    """
    OPEN/RELAX phase:
    - Freeze on first frame (no red text) for PREROLL_S
    - Then show red "Open/relax your hand!" while playing the video
    - Freeze on final frame for the full `duration` (your break length)
    """
    global exit_flag
    open_video_path = os.path.join(script_dir, "../Videos/Handopen2.mp4")
    cap = cv2.VideoCapture(open_video_path)
    if not cap.isOpened():
        print(f"Could not load hand open video: {open_video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1e-3:
        fps = 30.0
    delay_ms = int(1000.0 / fps)

    # Read first frame
    ret, frame = cap.read()
    if not ret:
        cap.release()
        print("No valid frame found in hand open video.")
        return
    first_frame = cv2.resize(frame, (720, 720))

    # Title once
    label = "Wait to Open Hand..."

    # --- Freeze on FIRST frame (no red text yet) ---
    start = time.time()
    while time.time() - start < PREROLL_S:
        overlay = first_frame.copy()

        # Title (black)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(overlay, label, 
                    ((overlay.shape[1] - cv2.getTextSize(label, font, 1.2, 3)[0][0]) // 2, 60),
                    font, 1.2, (0, 0, 0), 3)

        # Progress
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(overlay, progress)

        cv2.imshow("Display", overlay)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            exit_flag = True
            cap.release()
            return

    # Start classification when red text shows
    send_gesture_classification(1)

    # --- PLAYBACK with RED instruction text ---
    last_frame = first_frame
    while True:
        if ret:
            curr = frame
        else:
            ret, frame = cap.read()
            if not ret:
                break
            curr = frame

        resized = cv2.resize(curr, (720, 720))
        last_frame = resized.copy()

        # Title (black)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(resized, label, 
                    ((resized.shape[1] - cv2.getTextSize(label, font, 1.2, 3)[0][0]) // 2, 60),
                    font, 1.2, (0, 0, 0), 3)

        # RED instruction
        instruct = "Open/relax your hand!"
        tsize, _ = cv2.getTextSize(instruct, font, 1.5, 3)
        cv2.putText(resized, instruct, 
                    ((resized.shape[1] - tsize[0]) // 2, 120),
                    font, 1.5, (0, 0, 255), 3)
        #Audio for open hand
        announce_instruction("OPEN HAND")
        # Progress bar
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(resized, progress)

        cv2.imshow("Display", resized)
        if cv2.waitKey(delay_ms) & 0xFF == ord('q'):
            exit_flag = True
            cap.release()
            return

        ret, frame = cap.read()

    cap.release()

    # --- Freeze on LAST frame for full `duration` (break window) ---
    hold_start = time.time()
    while time.time() - hold_start < duration:
        overlay = last_frame.copy()

        # Title
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(overlay, label, 
                    ((overlay.shape[1] - cv2.getTextSize(label, font, 1.2, 3)[0][0]) // 2, 60),
                    font, 1.2, (0, 0, 0), 3)

        # RED instruction
        instruct = "STAY OPEN/RELAXED!"
        tsize, _ = cv2.getTextSize(instruct, font, 1.5, 3)
        cv2.putText(overlay, instruct, 
                    ((overlay.shape[1] - tsize[0]) // 2, 120),
                    font, 1.5, (0, 0, 255), 3)

        # Progress bar
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(overlay, progress)

        cv2.imshow("Display", overlay)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            exit_flag = True
            return

def draw_progress_bar(frame, progress, max_width=200, height=20):
    """
    Draws a progress bar at the top-right of the given frame.
    `progress` should be a float between 0 and 1.
    """
    h, w, _ = frame.shape
    x_start = w - max_width - 30
    y_start = h - height - 30
    
    # Outline
    cv2.rectangle(frame, (x_start, y_start), (x_start + max_width, y_start + height), (0, 0, 0), 2)

    # Fill
    fill_width = int(progress * max_width)
    cv2.rectangle(frame, (x_start, y_start), (x_start + fill_width, y_start + height), (0, 128, 0), -1)

def show_instructions(record_data_event):
    global exit_flag

    ensure_window_on_top(WINDOW_NAME)

    font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_page(lines):
        frame = np.full((800, 1000, 3), 245, dtype=np.uint8)
        y = 100
        for line, color in lines:
            text_size, _ = cv2.getTextSize(line, font, 1, 2)
            x = (frame.shape[1] - text_size[0]) // 2
            cv2.putText(frame, line, (x, y), font, 1, color, 2)
            y += 60
        return frame

    # Page 1
    page1 = [
        ("Welcome to the Symbionics Calibration Video!", (0, 0, 0)),
        ("", (0, 0, 0)),
        ("This process will help train the system to recognize", (0, 0, 0)),
        ("your unique brain signals for each hand gesture.", (0, 0, 0)),
        ("", (0, 0, 0)),
        ("Each hand action will be shown as a short video.", (0, 0, 0)),
        ("You will be asked to perform the same gesture.", (0, 0, 0)),
        ("A beeping sound will occur during the action", (0, 0, 0)),
        ("Try to imagine yourself opening/closing your hand", (0, 0, 0)),
        ("", (0, 0, 0)),
        ("Press ENTER to continue to the next page...", (0, 0, 0)),
        ("Press Q to quit at any time.", (0, 0, 0))
    ]

    # Page 2 (with red line)
    page2 = [
        ("Instruction Summary:", (0, 0, 0)),
        ("", (0, 0, 0)),
        ("1. Watch the hand gesture video.", (0, 0, 0)),
        ("2. When instructed in RED, ", (0, 0, 255)),  # RED
        (" perform/imagine yourself opening/closing your hand.", (0, 0, 0)),
        ("3. Hold the gesture for 10s until the next screen.", (0, 0, 0)),
        ("4. Repeat 2 and 3 until program ends.", (0, 0, 0)),
        ("", (0, 0, 0)),
        ("Press ENTER to continue to the next page...", (0, 0, 0)),
        ("Press Q to quit.", (0, 0, 0))
    ]

    # Page 3
    page3 = [
        ("Reminder for the entire process:", (0, 0, 0)),
        ("", (0, 0, 0)),
        (" - Sit comfortably with your back straight.", (0, 0, 0)),
        (" - Keep your arm and hand relaxed on a surface.", (0, 0, 0)),
        (" - Minimize facial movement and eye blinks.", (0, 0, 0)),
        (" - Keep your eyes fixated on the screen.", (0, 0, 0)),
        (" - Avoid jaw clenching or unnecessary muscle tension.", (0, 0, 0)),
        (" - Motor imagery - Imagination is key!", (0, 0, 0)),
        ("", (0, 0, 0)),
        ("We're about to begin the session.", (0, 0, 0)),
        ("Press ENTER to begin.", (0, 0, 0)),
        ("Press Q to quit.", (0, 0, 0))
    ]

    # --- Show Page 1 ---
    cv2.imshow("Display", draw_page(page1))
    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == ord('\r') or key == 13:
            break
        elif key == ord('q'):
            exit_flag = True
            return

    # --- Show Page 2 ---
    cv2.imshow("Display", draw_page(page2))
    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == ord('\r') or key == 13:
            break
        elif key == ord('q'):
            exit_flag = True
            return

    # --- Show Page 3 ---
    cv2.imshow("Display", draw_page(page3))
    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == ord('\r') or key == 13:
            record_data_event.set()
            print(record_data_event)
            break
        elif key == ord('q'):
            exit_flag = True
            return

def send_gesture_classification(code):
    global gesture_code, gesture_code_lock
    with gesture_code_lock:
        gesture_code = code

def get_gesture_code():
    global gesture_code, gesture_code_lock
    with gesture_code_lock:
        return gesture_code 

def calibrate(record_data_event):
    global exit_flag
    # --- MAIN LOOP ---
    show_instructions(record_data_event)
    if exit_flag == True:
        exit_flag = False
        print("exit flag in calibrate triggered")
        cv2.destroyAllWindows()
        return
    global session_start, cycle_count, count
    session_start = time.time()

    # while time.time() - session_start < total_duration:
    while count < cycle_count:
        play_balanced_videos_for(cycle_duration)
        if exit_flag == True:
            exit_flag = False
            cv2.destroyAllWindows()
            return
        # if (time.time() - session_start > total_duration):
        #     break
        print("[BREAK] Taking a break...")
        break_timestamp = int(time.time() * 1000)  # 13-digit ms precision

        show_break(break_duration)
        if exit_flag == True:
            exit_flag = False
            cv2.destroyAllWindows()
            return
        count += 1
    print("=== Session Complete ===")
    print("Video play counts:")
    for video, count in play_counts.items():
        print(f"{os.path.basename(video)}: {count}")
    count = 0
    cv2.destroyAllWindows()

def main():
    record = threading.Event()
    calibrate(record)
if __name__== "__main__":
    main()