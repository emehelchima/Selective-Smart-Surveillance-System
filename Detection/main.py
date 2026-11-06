import cv2
import json
import numpy as np

from pathlib import Path

from detection_engine import PersonZoneDetector


# ==================================
# 1. CONFIGURATION
# ==================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "best.pt"

VIDEO_PATH = BASE_DIR / "WhatsApp Video 2026-11-04 at 3.23.50 PM.mp4"

TRACKER_PATH = BASE_DIR / "trackers" / "custom_bytetrack.yaml"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

ZONE_ID = "restricted_zone_1"

CONFIDENCE = 0.15

ZONE_FILE = OUTPUT_DIR / "restricted_zone.json"
EVENT_FILE = OUTPUT_DIR / "zone_events.json"
OUTPUT_VIDEO = OUTPUT_DIR / "zone_monitoring.mp4"


# ==================================
# 2. CHECK REQUIRED FILES
# ==================================

for file_path in [MODEL_PATH, VIDEO_PATH, TRACKER_PATH]:

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )


# ==================================
# 3. SELECT RESTRICTED ZONE
# ==================================

zone_points = []

drawing_frame = None


def handle_mouse(event, x, y, flags, param):

    global zone_points

    if event == cv2.EVENT_LBUTTONDOWN:

        zone_points.append([x, y])

    elif event == cv2.EVENT_RBUTTONDOWN:

        if zone_points:
            zone_points.pop()


cap = cv2.VideoCapture(str(VIDEO_PATH))

if not cap.isOpened():
    raise RuntimeError("Could not open video.")


ret, first_frame = cap.read()

if not ret:
    raise RuntimeError("Could not read first video frame.")


drawing_frame = first_frame.copy()

cv2.namedWindow("Select Restricted Zone")

cv2.setMouseCallback(
    "Select Restricted Zone",
    handle_mouse
)


print("\nZONE SELECTION INSTRUCTIONS")
print("Left-click: Add a zone corner")
print("Right-click: Undo last corner")
print("C: Clear all points")
print("ENTER: Confirm zone")
print("ESC: Cancel\n")


while True:

    display = drawing_frame.copy()

    for point in zone_points:

        cv2.circle(
            display,
            tuple(point),
            6,
            (0, 255, 255),
            -1
        )

    if len(zone_points) > 1:

        cv2.polylines(
            display,
            [np.array(zone_points, dtype=np.int32)],
            False,
            (0, 255, 255),
            2
        )

    if len(zone_points) >= 3:

        cv2.polylines(
            display,
            [np.array(zone_points, dtype=np.int32)],
            True,
            (0, 255, 0),
            2
        )

    cv2.imshow(
        "Select Restricted Zone",
        display
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("c"):

        zone_points.clear()

    elif key == 13:

        if len(zone_points) >= 3:
            break

        print("Select at least 3 points.")

    elif key == 27:

        cap.release()
        cv2.destroyAllWindows()

        raise SystemExit(
            "Zone selection cancelled."
        )


cv2.destroyWindow("Select Restricted Zone")


# Save zone configuration

with open(ZONE_FILE, "w") as f:

    json.dump(
        {
            "zone_id": ZONE_ID,
            "points": zone_points
        },
        f,
        indent=4
    )


print("Restricted zone saved successfully.")


# ==================================
# 4. INITIALIZE DETECTION ENGINE
# ==================================

print("\nInitializing detection engine...")

detector = PersonZoneDetector(
    model_path=MODEL_PATH,
    tracker_path=TRACKER_PATH,
    confidence=CONFIDENCE,
    zone_id=ZONE_ID
)

print("Detection engine initialized successfully.")


# ==================================
# 5. PREPARE VIDEO OUTPUT
# ==================================

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30.0


width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)


writer = cv2.VideoWriter(
    str(OUTPUT_VIDEO),
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)


if not writer.isOpened():

    cap.release()

    raise RuntimeError(
        "Could not create output video."
    )


# ==================================
# 6. PROCESS VIDEO
# ==================================

zone_events = []

print("\nStarting person detection and tracking...")


try:

    while True:

        ret, frame = cap.read()

        if not ret:
            break


        # Send frame to detection engine

        annotated_frame, events = detector.process_frame(
            frame=frame,
            zone_points=zone_points,
            fps=fps
        )


        # Collect generated events

        for event in events:

            zone_events.append(event)

            print(
                f"{event['event'].upper()} | "
                f"Track ID: {event['track_id']} | "
                f"Zone: {event['zone_id']}"
            )


        # Display alerts

        if events:

            for event in events:

                if event["event"] == "zone_entry":

                    alert_text = (
                        f"INTRUSION ALERT! "
                        f"Person ID: {event['track_id']}"
                    )

                    cv2.putText(
                        annotated_frame,
                        alert_text,
                        (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )


        # Display video

        cv2.imshow(
            "Selective Smart Surveillance",
            annotated_frame
        )


        # Save processed video

        writer.write(annotated_frame)


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


finally:

    cap.release()

    writer.release()

    cv2.destroyAllWindows()


# ==================================
# 7. SAVE EVENTS
# ==================================

with open(EVENT_FILE, "w") as f:

    json.dump(
        zone_events,
        f,
        indent=4
    )


print("\nPROCESSING COMPLETED")

print(f"Total zone events: {len(zone_events)}")

print(f"Zone configuration: {ZONE_FILE}")

print(f"Zone events: {EVENT_FILE}")

print(f"Annotated video: {OUTPUT_VIDEO}")