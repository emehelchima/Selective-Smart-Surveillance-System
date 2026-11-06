# Backend Integration Contract

This document describes what the frontend expects from the backend. It is a hand-off guide, not a backend implementation.

## A. Camera frame

Provide the current camera frame to the Streamlit session:

```python
st.session_state["camera_frame"] = pillow_image
```

A NumPy image array is also accepted. The region editor displays the frame on a 960 × 540 canvas with aspect ratio preserved and padding if needed.

## B. Restricted region

After the operator clicks **Save Restricted Region**, the frontend stores:

```python
st.session_state["saved_region"]
```

The object includes:

- `shape`: `polygon` or `rectangle`
- `canvas_width`: 960
- `canvas_height`: 540
- `drawing`: raw JSON returned by the drawing component
- `coordinate_system`: top-left canvas origin, pixel coordinate space

The `drawing` value is a Fabric.js canvas JSON object. The backend developer must parse it and convert the geometry to the model's required format. Validate that the backend uses the same frame geometry. If the phone/camera moves, the region may no longer align.

## C. Event records

Populate:

```python
st.session_state["events"] = event_list
```

Each event dictionary should provide:

| Field | Expected value |
|---|---|
| `id` | Unique event identifier |
| `event_type` | Event category |
| `recognition` | Recognition result/status |
| `timestamp` | Python datetime or displayable string |
| `area` | Restricted area name |
| `status` | Alert/event status |
| `image` | Pillow image, usable image path, or `None` |
| `description` | Optional explanatory text |

## D. Camera and monitoring controls

The current UI controls are demo-only. Agree the backend function names/API first, then replace the demo state changes with the real camera connect/disconnect and monitoring start/stop calls.

## E. Important

The frontend does not implement the detection model, recognition, alert delivery, camera transport, or permanent database storage. Those remain backend responsibilities.
