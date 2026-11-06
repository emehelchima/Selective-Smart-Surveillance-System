# Smart Surveillance System — Frontend

This folder contains the Streamlit frontend for the group's Smart Surveillance System.

## Included pages

1. **Dashboard** — overview of camera/monitoring/region status and recent event records.
2. **Live Monitoring** — camera-frame preview, monitoring controls, and a real drawing canvas for a polygon or rectangle restricted region.
3. **Event History** — searchable event records with CSV export.
4. **Camera Settings** — fields for camera source, stream address, and camera name.

## Important project boundary

This is the **frontend deliverable**. The following functions still need to be supplied and connected by the backend team:

- Receiving the Android phone camera stream.
- Person/intrusion detection and recognition.
- Starting and stopping the actual detection pipeline.
- Capturing evidence images and generating real alerts.
- Saving event history permanently.

The Dashboard's Connect/Disconnect and Start/Stop demo controls only change the displayed demo status. The sample event records are illustrative, not actual detections.

## Installation

Use Python 3.13 or a compatible Python version supported by your installed Streamlit release. The current package requirements specify Python 3.10+ for the drawing component; the latest Streamlit documentation lists Python 3.14 support as well.

Open Command Prompt in this folder and run:

```bash
py -m pip install -r requirements.txt
```

Then start the interface:

```bash
py -m streamlit run Interface.py
```

Streamlit will display a local address in Command Prompt and usually open the app in your browser.

## How to test restricted-region drawing

1. Open **Live Monitoring**.
2. Upload a still image from the camera if the backend feed is not connected yet. If you do not upload one, a sample placeholder frame is shown.
3. Choose **Polygon** or **Rectangle**.
4. For a polygon, click around the boundary and click the first point to close the shape.
5. For a rectangle, click and drag.
6. Click **Save Restricted Region**.
7. Download `restricted_region.json` to share the selected region data with the backend developer.

The drawing is made over the displayed still frame. The backend must use the same frame dimensions and coordinate interpretation. If the camera moves or its view changes, the operator should review and save the region again.

## What is inside the region JSON?

The saved JSON contains:
- Shape type (`polygon` or `rectangle`).
- Canvas width and height.
- The raw drawing object returned by the canvas component.
- Save timestamp.
- A note about the coordinate system and camera-view stability.

The raw drawing object is preserved rather than guessing at point coordinates. The backend developer should parse the Fabric.js drawing object and convert it into the coordinate format required by the detection model.

## Backend integration hand-off

### 1. Camera frame

The interface looks for a camera frame in:

```python
st.session_state["camera_frame"]
```

The value can be a Pillow `Image` or a NumPy image array. The backend should update this value with the frame to be displayed. For region setup, the frame is fitted into a 960 × 540 canvas.

### 2. Event history

The interface reads event records from:

```python
st.session_state["events"]
```

Each event should be a dictionary with these fields:

```python
{
    "id": "EVT-0001",
    "event_type": "Restricted Area Event",
    "recognition": "Unknown",
    "timestamp": datetime.now(),
    "area": "Restricted Region",
    "status": "Alert sent",
    "image": None,  # Pillow image, image path, or None
    "description": "Event description",
}
```

The backend should populate the list with real records. The initial records in the frontend are demo examples.

### 3. Restricted region

After the operator saves a region, it is available in:

```python
st.session_state["saved_region"]
```

The saved object includes:
- `shape`
- `canvas_width`
- `canvas_height`
- `drawing` (raw canvas JSON)

The backend should read and interpret this data. Do not assume the raw Fabric.js object is already in the exact format required by the detection model.

### 4. Start and stop monitoring

The current buttons update demo session-state values only:

```python
st.session_state["monitoring"]
st.session_state["camera_connected"]
```

Replace the demo button actions with calls to the backend's actual start/stop and camera-connection functions when the backend API is agreed.

## Suggested team integration checklist

- [ ] Agree the main app entry point and merge this interface into the group's repository.
- [ ] Backend supplies a camera frame to `st.session_state["camera_frame"]`.
- [ ] Confirm the camera frame dimensions and region-coordinate conversion.
- [ ] Connect the saved region to the detection pipeline.
- [ ] Connect Start/Stop controls to the backend.
- [ ] Supply real event records and evidence images.
- [ ] Test the full flow with the Android phone camera.

## Files

- `Interface.py` — Streamlit application.
- `requirements.txt` — Python packages required to run the interface.
- `BACKEND_INTEGRATION.md` — concise integration contract for the backend team.
