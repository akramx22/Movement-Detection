# THIS PROGRAM IS TO SELECT THE REGION OF INTEREST (ROI) OF DETECTION MANUALLY USING MATPLOTLIB, TO GET AS AN OUTPUT 4 VARIABLES IN THE TERMINAL: (x, y, w, h).

# THE OUTPUT OF THIS PROGRAM WILL BE AN OUTPUT FOR THE detection.py PROGRAM: x, y, width, height = 0, 420, 180, 290

# EXAMPLE OF EXECUTION: python ROI.py

import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

# Global variable to store ROI
roi = None

def line_select_callback(eclick, erelease):
    global roi
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)
    roi = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))  # (x, y, w, h)

def get_roi(frame):
    global roi
    fig, ax = plt.subplots(1)
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    toggle_selector = RectangleSelector(
        ax,
        onselect=line_select_callback,
        useblit=True,
        button=[1],  # left click only
        minspanx=5, minspany=5,
        spancoords='pixels',
        interactive=True
    )
    
    plt.show()
    return roi

# ---- Example usage ----
cap = cv2.VideoCapture("Cut0_20250819170023_20250819180023.avi")
ret, frame = cap.read()

# Select ROI on the first frame
roi = get_roi(frame)
print("Selected ROI:", roi)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if roi:
        x, y, w, h = roi
        roi_frame = frame[y:y+h, x:x+w]  # Crop only ROI

        # Example: grayscale view of ROI
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("ROI Frame", gray)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
