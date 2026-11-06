Selective Smart Surveillance System --- Detection and Zoning Module

Overview

This module is responsible for detecting people, tracking their
movement, and identifying when tracked people enter or leave a
user-defined restricted zone.


It is designed to work as one component of the larger Selective Smart
Surveillance System. Face recognition, access authorization, database
management, and alert generation are outside the scope of this module
and are handled by other components.


Responsibilities


Person detection: Uses a fine-tuned YOLO11 model to detect people in video frames.

Object tracking: Uses ByteTrack to assign tracking IDs and follow detected people across frames.

Restricted-zone monitoring: Lets the operator draw a polygon around the area to monitor.

Entry and exit detection: Checks each tracked person's foot-point against the polygon and records transitions into and out of the zone.

Event output: Saves zone configuration and detected events as JSON files.

Annotated video: Saves a video showing person detections, tracking IDs, and zone status.


Project Structure

The relevant files and folders are:


SelectiveSmartSurveillance/
├── main.py
├── best.pt
├── 19595834-hd_1920_1080_30fps.mp4
├── trackers/
│   └── custom_bytetrack.yaml
└── output/
    ├── restricted_zone.json
    ├── zone_events.json
    └── zone_monitoring.mp4

The video filename shown above is the current default configured in
main.py. Replace it with the filename of the team's test video when
needed.


Requirements


Python 3.12 (the project has been tested in a Python 3.12 environment)

OpenCV

NumPy

Ultralytics

PyTorch, installed in a version compatible with the installed Ultralytics package


Install the Python packages in your virtual environment:


python -m pip install ultralytics opencv-python numpy

Ultralytics will install or request compatible dependencies, including
PyTorch. If PyTorch installation fails, follow the official PyTorch
installation instructions for your operating system and hardware.


Setup


Open the project folder in Visual Studio Code.


Open a PowerShell terminal in the project folder.


Create a virtual environment if one does not already exist:

py -3.12 -m venv .venv

Activate it:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

Install the dependencies:

python -m pip install ultralytics opencv-python numpy

Confirm that the required files exist:

best.pt
trackers/custom_bytetrack.yaml
The input video configured by VIDEO_PATH in main.py


Configuration

At the beginning of main.py, the following settings control the run:


MODEL_PATH = Path("best.pt")
VIDEO_PATH = Path("19595834-hd_1920_1080_30fps.mp4")
TRACKER_PATH = Path("trackers/custom_bytetrack.yaml")

OUTPUT_DIR = Path("output")
ZONE_ID = "restricted_zone_1"
CONFIDENCE = 0.15


MODEL_PATH: location of the trained YOLO weights.

VIDEO_PATH: input video to process.

TRACKER_PATH: ByteTrack configuration file.

OUTPUT_DIR: folder for generated results.

ZONE_ID: identifier attached to events from the selected zone.

CONFIDENCE: minimum YOLO detection confidence used by the script.


To process the team's recorded video, update VIDEO_PATH to its
filename or path before running the program.


Running the Module

With the virtual environment activated, run:


python main.py

The program opens the input video and displays the first frame for zone
selection.


Selecting the restricted zone

Use the mouse and keyboard in the Select Restricted Zone window:


  Input         Action



  Left-click    Add a polygon corner
  Right-click   Undo the last corner
  C           Clear all selected corners
  Enter       Confirm the zone (at least three points required)
  Esc         Cancel zone selection


Choose points around the area to monitor. The polygon is saved in
output/restricted_zone.json.


After confirmation, the program loads the YOLO model and processes the
video. Press Q in the video window to stop processing early.


How Detection and Zone Monitoring Work


YOLO detects people in each video frame.

ByteTrack associates detections across frames and provides a tracking ID.

The bottom-centre point of each person's bounding box is calculated. This is the person's foot-point for the zone test.

OpenCV's polygon test determines whether that point is inside or outside the selected zone.

The program compares the current zone state with the previous state for that tracking ID:
Outside to inside: zone_entry
Inside to outside: zone_exit
No change: no transition event is recorded

The program annotates the frame and writes it to the output video.


A tracking ID identifies a tracked object during a processing run. It is
not a permanent identity for a real person and should not be treated as
one.


Output Files

The program creates or updates these files in output/:


restricted_zone.json

Stores the selected zone ID and polygon coordinates.


Example:


{
    "zone_id": "restricted_zone_1",
    "points": [
        [120, 180],
        [640, 170],
        [700, 520],
        [100, 530]
    ]
}

The coordinates above are illustrative; actual coordinates depend on the
selected video frame and the polygon drawn by the operator.


zone_events.json

Stores entry and exit events. Each event includes:



event: zone_entry or zone_exit

track_id: ByteTrack ID for the tracked person

zone_id: selected zone identifier

frame_number: frame where the transition was detected

timestamp_seconds: approximate video time of the event

recorded_at: time the event was processed and recorded


Example:


[
    {
        "event": "zone_entry",
        "track_id": 3,
        "zone_id": "restricted_zone_1",
        "frame_number": 250,
        "timestamp_seconds": 8.33,
        "recorded_at": "2026-11-04T15:00:00"
    }
]

This example is illustrative, not a result from a real test run.


zone_monitoring.mp4

An annotated output video showing: - The restricted-zone polygon -
Person bounding boxes - Tracking IDs - Foot-points - INSIDE ZONE or
OUTSIDE ZONE status - Frame counter


Integration Handover

This module provides detection, tracking, and zone-event information for
integration with the other system components.


The main handover data is in output/zone_events.json. Other modules
can use the track_id, zone_id, event type, frame number, and video
timestamp as integration inputs.


A track_id is only meaningful within the relevant tracking run. Other
modules should use the video/run context and timestamps when associating
information with it.


Testing Recommendations

Test the module with a video recorded by the project team, as requested
by the project facilitator. Use consenting participants and a clearly
marked test area.


Include scenarios such as:



A person remains outside the selected zone.

A person enters the selected zone.

A person exits after entering.

Two or more people move through the scene.

A person is briefly obstructed or leaves the camera view.


Review the annotated video and JSON events after each test. Compare the
events against what actually happened in the video.


Current Limitations


The current script processes one configured video per run.

The current script selects one polygon zone per run.

The zone ID is currently configured in main.py.

Zone testing uses the bottom-centre foot-point of each person bounding box.

Tracking IDs can change after occlusion, missed detections, or tracker resets.

The script records transitions based on detected frames; brief detection errors or foot-point movement near the polygon boundary may cause missed or extra transitions.

The selected polygon coordinates are tied to the input video's frame dimensions and camera view. They may not represent the same physical area in a different camera view.

The current module does not identify people, decide access permissions, manage a database, or send security alerts.


Scope Boundary

This module is limited to:



Person detection

Person tracking

User-defined restricted-zone selection

Zone entry and exit detection

Zone event export

Annotated video generation


Face recognition, identity verification, zone-specific authorization,
database management, and alert delivery are separate modules of the
overall system.


Troubleshooting

best.pt was not found - Confirm that best.pt is in the project
root or update MODEL_PATH.


The video cannot be opened - Confirm that the video exists and
update VIDEO_PATH. - Use a video format supported by the installed
OpenCV build.


ByteTrack configuration not found - Confirm that
trackers/custom_bytetrack.yaml exists at the configured path.


No people are detected - Check the video quality and camera view. -
Confirm that the correct model weights are loaded. - Review the
confidence setting in main.py.


The zone does not match the intended area - Draw the polygon again
on the first frame. - Remember that polygon coordinates are specific to
the video frame and camera view.



Module: Person Detection, Tracking, and Restricted-Zone Monitoring
Parent project: Selective Smart Surveillance SystemSelective Smart Surveillance System --- Detection and Zoning Module

Overview

This module is responsible for detecting people, tracking their
movement, and identifying when tracked people enter or leave a
user-defined restricted zone.


It is designed to work as one component of the larger Selective Smart
Surveillance System. Face recognition, access authorization, database
management, and alert generation are outside the scope of this module
and are handled by other components.


Responsibilities


Person detection: Uses a fine-tuned YOLO11 model to detect people in video frames.

Object tracking: Uses ByteTrack to assign tracking IDs and follow detected people across frames.

Restricted-zone monitoring: Lets the operator draw a polygon around the area to monitor.

Entry and exit detection: Checks each tracked person's foot-point against the polygon and records transitions into and out of the zone.

Event output: Saves zone configuration and detected events as JSON files.

Annotated video: Saves a video showing person detections, tracking IDs, and zone status.


Project Structure

The relevant files and folders are:


SelectiveSmartSurveillance/
├── main.py
├── best.pt
├── 19595834-hd_1920_1080_30fps.mp4
├── trackers/
│   └── custom_bytetrack.yaml
└── output/
    ├── restricted_zone.json
    ├── zone_events.json
    └── zone_monitoring.mp4

The video filename shown above is the current default configured in
main.py. Replace it with the filename of the team's test video when
needed.


Requirements


Python 3.12 (the project has been tested in a Python 3.12 environment)

OpenCV

NumPy

Ultralytics

PyTorch, installed in a version compatible with the installed Ultralytics package


Install the Python packages in your virtual environment:


python -m pip install ultralytics opencv-python numpy

Ultralytics will install or request compatible dependencies, including
PyTorch. If PyTorch installation fails, follow the official PyTorch
installation instructions for your operating system and hardware.


Setup


Open the project folder in Visual Studio Code.


Open a PowerShell terminal in the project folder.


Create a virtual environment if one does not already exist:

py -3.12 -m venv .venv

Activate it:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

Install the dependencies:

python -m pip install ultralytics opencv-python numpy

Confirm that the required files exist:

best.pt
trackers/custom_bytetrack.yaml
The input video configured by VIDEO_PATH in main.py


Configuration

At the beginning of main.py, the following settings control the run:


MODEL_PATH = Path("best.pt")
VIDEO_PATH = Path("19595834-hd_1920_1080_30fps.mp4")
TRACKER_PATH = Path("trackers/custom_bytetrack.yaml")

OUTPUT_DIR = Path("output")
ZONE_ID = "restricted_zone_1"
CONFIDENCE = 0.15


MODEL_PATH: location of the trained YOLO weights.

VIDEO_PATH: input video to process.

TRACKER_PATH: ByteTrack configuration file.

OUTPUT_DIR: folder for generated results.

ZONE_ID: identifier attached to events from the selected zone.

CONFIDENCE: minimum YOLO detection confidence used by the script.


To process the team's recorded video, update VIDEO_PATH to its
filename or path before running the program.


Running the Module

With the virtual environment activated, run:


python main.py

The program opens the input video and displays the first frame for zone
selection.


Selecting the restricted zone

Use the mouse and keyboard in the Select Restricted Zone window:


  Input         Action



  Left-click    Add a polygon corner
  Right-click   Undo the last corner
  C           Clear all selected corners
  Enter       Confirm the zone (at least three points required)
  Esc         Cancel zone selection


Choose points around the area to monitor. The polygon is saved in
output/restricted_zone.json.


After confirmation, the program loads the YOLO model and processes the
video. Press Q in the video window to stop processing early.


How Detection and Zone Monitoring Work


YOLO detects people in each video frame.

ByteTrack associates detections across frames and provides a tracking ID.

The bottom-centre point of each person's bounding box is calculated. This is the person's foot-point for the zone test.

OpenCV's polygon test determines whether that point is inside or outside the selected zone.

The program compares the current zone state with the previous state for that tracking ID:
Outside to inside: zone_entry
Inside to outside: zone_exit
No change: no transition event is recorded

The program annotates the frame and writes it to the output video.


A tracking ID identifies a tracked object during a processing run. It is
not a permanent identity for a real person and should not be treated as
one.


Output Files

The program creates or updates these files in output/:


restricted_zone.json

Stores the selected zone ID and polygon coordinates.


Example:


{
    "zone_id": "restricted_zone_1",
    "points": [
        [120, 180],
        [640, 170],
        [700, 520],
        [100, 530]
    ]
}

The coordinates above are illustrative; actual coordinates depend on the
selected video frame and the polygon drawn by the operator.


zone_events.json

Stores entry and exit events. Each event includes:



event: zone_entry or zone_exit

track_id: ByteTrack ID for the tracked person

zone_id: selected zone identifier

frame_number: frame where the transition was detected

timestamp_seconds: approximate video time of the event

recorded_at: time the event was processed and recorded


Example:


[
    {
        "event": "zone_entry",
        "track_id": 3,
        "zone_id": "restricted_zone_1",
        "frame_number": 250,
        "timestamp_seconds": 8.33,
        "recorded_at": "2026-11-04T15:00:00"
    }
]

This example is illustrative, not a result from a real test run.


zone_monitoring.mp4

An annotated output video showing: - The restricted-zone polygon -
Person bounding boxes - Tracking IDs - Foot-points - INSIDE ZONE or
OUTSIDE ZONE status - Frame counter


Integration Handover

This module provides detection, tracking, and zone-event information for
integration with the other system components.


The main handover data is in output/zone_events.json. Other modules
can use the track_id, zone_id, event type, frame number, and video
timestamp as integration inputs.


A track_id is only meaningful within the relevant tracking run. Other
modules should use the video/run context and timestamps when associating
information with it.


Testing Recommendations

Test the module with a video recorded by the project team, as requested
by the project facilitator. Use consenting participants and a clearly
marked test area.


Include scenarios such as:



A person remains outside the selected zone.

A person enters the selected zone.

A person exits after entering.

Two or more people move through the scene.

A person is briefly obstructed or leaves the camera view.


Review the annotated video and JSON events after each test. Compare the
events against what actually happened in the video.


Current Limitations


The current script processes one configured video per run.

The current script selects one polygon zone per run.

The zone ID is currently configured in main.py.

Zone testing uses the bottom-centre foot-point of each person bounding box.

Tracking IDs can change after occlusion, missed detections, or tracker resets.

The script records transitions based on detected frames; brief detection errors or foot-point movement near the polygon boundary may cause missed or extra transitions.

The selected polygon coordinates are tied to the input video's frame dimensions and camera view. They may not represent the same physical area in a different camera view.

The current module does not identify people, decide access permissions, manage a database, or send security alerts.


Scope Boundary

This module is limited to:



Person detection

Person tracking

User-defined restricted-zone selection

Zone entry and exit detection

Zone event export

Annotated video generation


Face recognition, identity verification, zone-specific authorization,
database management, and alert delivery are separate modules of the
overall system.


Troubleshooting

best.pt was not found - Confirm that best.pt is in the project
root or update MODEL_PATH.


The video cannot be opened - Confirm that the video exists and
update VIDEO_PATH. - Use a video format supported by the installed
OpenCV build.


ByteTrack configuration not found - Confirm that
trackers/custom_bytetrack.yaml exists at the configured path.


No people are detected - Check the video quality and camera view. -
Confirm that the correct model weights are loaded. - Review the
confidence setting in main.py.


The zone does not match the intended area - Draw the polygon again
on the first frame. - Remember that polygon coordinates are specific to
the video frame and camera view.



Module: Person Detection, Tracking, and Restricted-Zone Monitoring
Parent project: Selective Smart Surveillance System