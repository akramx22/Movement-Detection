''' THIS CODE IS THE MAIN DETECTION LOGIC, RUN IN A LOOP TO PROCESS ALL VIDEOS IN 'VIDEO_FOLDER' AND PERFORM DETECTION BETWEEN FRAMES EACH SECOND (DETECTION_INTERVAL) IN A SPECIFIC REGION OF INTEREST SELECTED BY 
x, y, width, height VARIABLES, WITH A SPECIFIC SENSIVITY LEVEL FOR BIG OBJECTS (MOVEMENT_THRESHOLD), ANY DETECTION WILL BE DETAILED IN THE TERMINAL AND A SCENE OF 10 SECONDS WILL BE CUT, 5 SECOND BEFORE THE SECOND
OF DETECTION AND 5 AFTER, AND IT WILL BE STORED IN 'OUTPUT_FOLDER'
'''
# NOTE: IF MULTIPLE DETECTIONS HAPPEND WITHIN 10 SECONDS, ONLY THE FIRST ONE WILL BE STORED TO AVOID DUPLICATE SCENES SINCE A SCENE OF 10 SECONDS WILL BE STORED WITH EACH DETECTION. 

# EXAMPLE OF EXECUTION: python detection.py


import cv2
import os
import numpy as np
import time

# --- CONFIGURATION ---
VIDEO_FOLDER = "Videos 08-25"
OUTPUT_FOLDER = "Detected 08-25"
MOVEMENT_THRESHOLD = 500000
DETECTION_INTERVAL = 1  # seconds

# Region of interest (bottom-left corner)
x, y, width, height = 0, 420, 180, 290

# Create output directory if not exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_clip(cap, fps, start_sec, duration_sec, output_path):
    start_frame = int(start_sec * fps)
    end_frame = int((start_sec + duration_sec) * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for _ in range(start_frame, end_frame):
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    out.release()

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    video_name = os.path.basename(video_path)
    video_stem = os.path.splitext(video_name)[0]
    print(f"\n🎞️ Processing: {video_name} ({int(duration//60)} min {int(duration%60)} sec)")

    prev_frame = None
    i = 0
    saved_intervals = []

    while True:
        frame_number = int(i * DETECTION_INTERVAL * fps)
        if frame_number >= total_frames:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = cap.read()
        if not ret:
            break

        corner = frame[y:y+height, x:x+width]
        gray = cv2.cvtColor(corner, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = np.abs(gray.astype(int) - prev_frame.astype(int))
            score = np.sum(diff)
            if score > MOVEMENT_THRESHOLD:
                detection_time = i * DETECTION_INTERVAL
                clip_start_time = max(detection_time - 5, 0)
                clip_end_time = clip_start_time + 10

                # Check for overlap
                if not any(abs(clip_start_time - start) < 10 for start, _ in saved_intervals):
                    saved_intervals.append((clip_start_time, clip_end_time))
                    clip_filename = f"{video_stem}_clip_{int(clip_start_time)}s.avi"
                    output_path = os.path.join(OUTPUT_FOLDER, clip_filename)
                    extract_clip(cap, fps, clip_start_time, 10, output_path)

                    minutes = int(detection_time // 60)
                    seconds = int(detection_time % 60)
                    print(f"⚠️ Movement detected at {minutes:02}:{seconds:02} ➜ Saved: {clip_filename}")

        prev_frame = gray
        i += 1

    cap.release()
    print("✅ Finished:", video_name)

# --- PROCESS ALL VIDEOS IN FOLDER ---

start_time = time.time()

video_files = sorted([
    os.path.join(VIDEO_FOLDER, f)
    for f in os.listdir(VIDEO_FOLDER)
    if f.lower().endswith('.avi')
])

if not video_files:
    print("⚠️ No video files found.")
else:
    for video in video_files:
        process_video(video)

end_time = time.time()
elapsed = end_time - start_time
h = int(elapsed // 3600)
m = int((elapsed % 3600) // 60)
s = int(elapsed % 60)

print(f"\n🎬 All videos processed.")
print(f"⏱️ Total execution time: {h:02d}:{m:02d}:{s:02d}")
