# Alerting and security module

This module replaces the Telegram delivery step with an in-app notification feed. It is a standalone integration slice because no surveillance application source repository was present in the supplied workspace.

## What it does

- Stores event metadata in a local SQLite database and captured face/full-frame images in local files.
- Creates an in-app notification only when the recognition result is `unknown`.
- Applies a 60-second default cooldown per zone and tracking ID. Events still get logged while an alert is suppressed.
- Shows new notifications in the Streamlit dashboard while it is open, with a two-second refresh interval.
- Deletes event rows and their images after the configured retention period, defaulting to 30 days.
- Uses generated image filenames, restrictive local file permissions where supported, and environment-based storage configuration.

Unknown or inconclusive recognition is only a recognition result. It is not treated as proof that a person is an intruder or a threat.

## Start the dashboard

Use Python 3.10 or newer. From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py --server.address 127.0.0.1
```

The dashboard is intentionally bound to localhost. Do not expose captured face images or the dashboard on a shared network without adding authentication and access controls.

## Connect the surveillance pipeline

The event manager should call `AlertingService.record_event` after a boundary crossing and recognition attempt. Pass the recognition result, zone, temporary tracker ID, and image bytes when available:

```python
from alerting import service_from_environment

alerts = service_from_environment()
saved = alerts.record_event(
    known=False,                  # True / False / None (inconclusive)
    confidence=0.42,
    zone="server-room-door",
    track_id="track-17",
    occurred_at="2026-11-01T10:15:00Z",
    face_status="captured",      # or a reason such as "face_not_visible"
    face_image=face_jpeg_bytes,   # optional bytes
    full_frame=frame_jpeg_bytes,  # optional bytes
)
print(saved['alert_status'])      # notified, cooldown, or not_applicable
```

Use `known=True` for an enrolled match, `known=False` for unknown/no match, and `known=None` for unavailable or inconclusive recognition. Only the `False` result can produce an in-app notification. A stable tracker ID is required for per-person cooldown; if omitted, each unknown event is eligible for a notification.

The service returns `notified` when the event is made visible in the dashboard feed. The pipeline does not need a Telegram bot token or internet connection for local notifications. Call `list_events()` to read the event history from another local component.

## Configuration and data handling

Copy `.env.example` to `.env` and load it with your preferred environment loader, or set the variables in the process environment:

- `SURVEILLANCE_DB`: SQLite file location.
- `SURVEILLANCE_IMAGE_DIR`: directory for face and full-frame captures.
- `ALERT_COOLDOWN_SECONDS`: per-track notification cooldown.
- `IMAGE_RETENTION_DAYS`: automatic local retention period.

The default `data/` directory is ignored by Git. Captures contain sensitive images: restrict account access, use authorized demo subjects, document consent, and verify deletion/retention rules with the institution before real use. Local filesystem permissions are best-effort and depend on the operating system.

## Integration boundary

This module assumes the vision system already emits a crossing event and a recognition result. It does not perform person detection, face recognition, user authentication, or remote browser push while the dashboard is closed. The current app notification appears in the open dashboard; persistent offline browser notifications would require a service worker and a push-delivery service.
