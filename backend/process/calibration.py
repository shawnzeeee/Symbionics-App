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
    "Handclose2.mp4": "Wait to Close Hand...",
}

cycle_duration = 8   
break_duration = 12    
#total_duration = 60 * 3
total_duration = 20
cycle_count = 2
count = 0

exit_flag = False

exit_flag = False

gesture_code = 0
gesture_code_lock = threading.Lock()

# --- HELPER FUNCTIONS ---
def get_least_played_video():
    min_play = min(play_counts.values())
    candidates = [v for v in video_list if play_counts[v] == min_play]
    chosen = random.choice(candidates)
    play_counts[chosen] += 1
    return chosen

previous_class = 0

def play_video_then_countdown(path, gesture_index):
    global exit_flag
    global exit_flag
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"Cannot open: {path}")
        return

    frame_rate = 60
    frame_rate = 60
    last_frame = None
    cv2.namedWindow("Display", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Display", 720, 720)
    
    # --- Play the video and remember the last frame ---
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        last_frame = frame.copy()
        
        resized_frame = cv2.resize(frame, (720, 720))

        # Draw custom title
        filename = os.path.basename(path)
        label = gesture_labels.get(filename, filename)
        # --- Draw centered label with box ---
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        text_size, baseline = cv2.getTextSize(label, font, font_scale, thickness)
        text_width, text_height = text_size

        # Center position
        center_x = resized_frame.shape[1] // 2
        text_x = center_x - text_width // 2
        text_y = 60  # distance from top

        # Draw background rectangle
        box_padding = 10
        top_left = (text_x - box_padding, text_y - text_height - box_padding)
        bottom_right = (text_x + text_width + box_padding, text_y + baseline + box_padding)
        cv2.rectangle(resized_frame, top_left, bottom_right, (255, 255, 255), -1)  # White box
        cv2.rectangle(resized_frame, top_left, bottom_right, (0, 0, 0), 2)         # Black border

        # Draw label text
        cv2.putText(resized_frame, label, (text_x, text_y), font,
                    font_scale, (0, 0, 0), thickness)
        
        # Calculate progress bar based on cycle count
        global count, cycle_count
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(resized_frame, progress)
        
        cv2.imshow("Display", resized_frame)
        last_frame = resized_frame.copy()

        if cv2.waitKey(int(1500 // frame_rate)) & 0xFF == ord('q'):
            exit_flag = True
            return
    
            exit_flag = True
            return
    
    cap.release()

    if last_frame is None:
        print("Error: No valid frame captured.")
        return

    h, w, _ = last_frame.shape
    x = int(w * 0.75) - 30  # 75% across width
    y = int(h / 2) + 20     # Vertically centered

    # --- Show 3..2..1 countdown on the last frame ---
    skip_countdown = True  # Set to True to skip countdown and jump to GO
    send_gesture_classification(2)

    send_gesture_classification(2)

    for i in (["GO"] if skip_countdown else [3, 2, 1, "GO"]):
        overlay = last_frame.copy()

        # --- Title box (reuse your existing title drawing code if needed) ---
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale_title = 1.2
        thickness_title = 3
        text_size_title, baseline_title = cv2.getTextSize(label, font, font_scale_title, thickness_title)
        text_width_title, text_height_title = text_size_title
        center_x = overlay.shape[1] // 2
        text_x_title = center_x - text_width_title // 2
        text_y_title = 60

        top_left_title = (text_x_title - 10, text_y_title - text_height_title - 10)
        bottom_right_title = (text_x_title + text_width_title + 10, text_y_title + baseline_title + 10)
        cv2.rectangle(overlay, top_left_title, bottom_right_title, (255, 255, 255), -1)
        cv2.rectangle(overlay, top_left_title, bottom_right_title, (0, 0, 0), 2)
        cv2.putText(overlay, label, (text_x_title, text_y_title), font, font_scale_title, (0, 0, 0), thickness_title)

        # --- Countdown just below title ---
        font_scale_countdown = 2.0
        thickness_countdown = 4
        countdown_text = str(i)
        text_size, baseline = cv2.getTextSize(countdown_text, font, font_scale_countdown, thickness_countdown)
        text_width, text_height = text_size

        text_y = text_y_title + 80  # adjust spacing between title and countdown
        text_x = center_x - text_width // 2

        top_left = (text_x - 10, text_y - text_height - 10)
        bottom_right = (text_x + text_width + 10, text_y + baseline + 10)
        cv2.rectangle(overlay, top_left, bottom_right, (255, 255, 255), -1)
        cv2.rectangle(overlay, top_left, bottom_right, (0, 0, 0), 2)
        cv2.putText(overlay, countdown_text, (text_x, text_y+10), font, font_scale_countdown, (0, 0, 0), thickness_countdown)
        
        # Progress bar for overlay
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(overlay, progress)

        cv2.imshow("Display", overlay)

        if i == "GO":
            timestamp = int(time.time() * 1000)  # 13-digit ms precision
            filename = os.path.basename(path)
            label = gesture_labels.get(filename, filename)
            class_index = video_list.index(path)
            # Show hold message for 8 seconds (no class 16 sent)
            hold_frame = overlay.copy()
            hold_text = "Hold the gesture!"
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size, _ = cv2.getTextSize(hold_text, font, 1.5, 3)
            text_x = (hold_frame.shape[1] - text_size[0]) // 2
            text_y = 120
            cv2.putText(hold_frame, hold_text, (text_x, text_y), font, 1.5, (0, 0, 255), 3)
            for _ in range(8):
                cv2.imshow("Display", hold_frame)
                if cv2.waitKey(1000) & 0xFF == ord('q'):
                    exit_flag = True
                    return
                    exit_flag = True
                    return
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            exit_flag = True
            return
            exit_flag = True
            return

    # --- Hold last frame for 2 seconds ---
    progress = min(count / cycle_count, 1.0) if cycle_count else 0
    draw_progress_bar(last_frame, progress)
    
    cv2.imshow("Display", last_frame)
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        exit_flag = True
        return
        exit_flag = True
        return

    # Do NOT destroy the window here — reused across calls

def play_balanced_videos_for(duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        video_path = get_least_played_video()
        gesture_index = video_list.index(video_path)
        timestamp = int(time.time())
        play_order.append((video_path, timestamp))
        #print(f"[PLAY] {os.path.basename(video_path)} (index: {gesture_index + 1})")
        play_video_then_countdown(video_path, gesture_index)
        if time.time() - start_time >= duration:
            break
        
def show_break(duration):
    global exit_flag
    # Load hand open video
    open_video_path = os.path.join(script_dir, "../Videos/Handopen2.mp4")
    cap = cv2.VideoCapture(open_video_path)
    last_frame = None
    fps = 30
    delay = int(1000 / fps) if fps > 0 else 33

    if not cap.isOpened():
        print(f"Could not load hand open video: {open_video_path}")
        return

    # --- Step 1: Play video frames with progress bar ---
    global count, cycle_count
    progress = min(count / cycle_count, 1.0) if cycle_count else 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (720, 720))
        last_frame = frame.copy()

        # Draw label at top center
        font = cv2.FONT_HERSHEY_SIMPLEX
        label = "Wait to Open Hand..."
        text_size, baseline = cv2.getTextSize(label, font, 1.2, 3)
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = 60
        cv2.putText(frame, label, (text_x, text_y), font, 1.2, (0, 0, 0), 3)

        # Draw progress bar on video frame
        draw_progress_bar(frame, progress)
        cv2.imshow("Display", frame)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            exit_flag = True
            return

    cap.release()

    if last_frame is None:
        print("No valid frame found in hand open video.")
        return

    # --- Step 2: Freeze last frame and show countdown with progress bar ---
    start = time.time()
    send_gesture_classification(1)


    while time.time() - start < duration:
        remaining = math.ceil(duration - (time.time() - start))
        display_frame = last_frame.copy()
        
        #label at top
        font = cv2.FONT_HERSHEY_SIMPLEX
        label = "Wait to Open Hand..."
        text_size, baseline = cv2.getTextSize(label, font, 1.2, 3)
        text_x = (display_frame.shape[1] - text_size[0]) // 2
        text_y = 60
        cv2.putText(display_frame, label, (text_x, text_y), font, 1.2, (0, 0, 0), 3)

        # Text and updated progress
        font = cv2.FONT_HERSHEY_SIMPLEX
        hold_text = "Open/relax your hand!"
        text_size, _ = cv2.getTextSize(hold_text, font, 1.5, 3)
        text_x = (display_frame.shape[1] - text_size[0]) // 2
        text_y = 120
        cv2.putText(display_frame, hold_text, (text_x, text_y), font, 1.5, (0, 0, 255), 3)
        progress = min(count / cycle_count, 1.0) if cycle_count else 0
        draw_progress_bar(display_frame, progress)
        
        cv2.imshow("Display", display_frame)
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            exit_flag = True
            return
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
        ("", (0, 0, 0)),
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
        ("4. Open/relax your hand for 10s during the next video.", (0, 0, 0)),
        ("5. Repeat 3 and 4 until program ends.", (0, 0, 0)),
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
    global exit_flag
    # --- MAIN LOOP ---
    show_instructions(record_data_event)
    if exit_flag == True:
        exit_flag = False
        cv2.destroyAllWindows()
        return
    if exit_flag == True:
        exit_flag = False
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

# def main():
#     record = threading.Event()
#     calibrate(record)
# if __name__== "__main__":
#     main()