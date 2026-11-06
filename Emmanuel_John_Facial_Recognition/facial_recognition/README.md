# Facial Recognition Module

Implemented by Emmanuel John for the Group Selective Surveillance
System for Security.

## Purpose

Enroll people using a first name and surname, store face embeddings,
and return Known, Unknown, or Uncertain decisions.

Uses pretrained OpenCV YuNet and SFace models. No model weights have
been trained or fine-tuned in this work.

## Folder layout

Keep this package inside the main project:

project/
├── facial_recognition/
│   ├── __init__.py
│   ├── config.py
│   ├── face_processing.py
│   ├── gallery.py
│   ├── recognition.py
│   └── requirements.txt
├── models/
└── private_data/

## Installation

Run from the project folder:

```bash
python -m pip install -r facial_recognition/requirements.txt
```

Use a separate Python environment. The module targets OpenCV 4.
It does not require a GPU.

## Pretrained models

Download these files into models/:

- face_detection_yunet_2023mar.onnx
- face_recognition_sface_2021dec.onnx

Official download URLs:

https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx

https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx

Credit: OpenCV Zoo and the YuNet/SFace model authors.
Consult each model directory's license before redistribution.

## Enrollment

Run from the project folder:

```python
import cv2
from facial_recognition.face_processing import FaceProcessor
from facial_recognition.gallery import FaceGallery

processor = FaceProcessor("models")
gallery = FaceGallery()

photo = cv2.imread("private_data/reference.jpg")
embedding, _ = processor.extract(photo)

gallery.enroll("Emmanuel", "John", embedding)
gallery.save("private_data/enrollment_gallery_v2.json")
```

For later enrollment sessions, load the existing gallery first
instead of creating an empty one:

```python
gallery = FaceGallery.load("private_data/enrollment_gallery_v2.json")
```

## Recognition

```python
from facial_recognition.recognition import FaceRecognitionService

service = FaceRecognitionService(processor, gallery)

new_photo = cv2.imread("private_data/test.jpg")
result = service.recognize(new_photo)

print(result["status"])
print(result["name"])
print(result["similarity"])
print(result["reason"])
```

## Integration contract

Input: a nonempty uint8 BGR image containing exactly one detectable face.

The tracking module should supply a suitable image crop with enough
context for face detection. Avoid an excessively tight crop.

Output:
- status: Known, Unknown, or Uncertain
- name: accepted full name, or None
- candidate: closest reference, even if rejected
- similarity: cosine similarity, not a probability
- threshold: current acceptance threshold
- score_gap: difference between the two best identity scores
- required_margin: minimum separation between candidates
- reason: explanation of the decision
- scores: similarities for all enrolled people

A candidate is not a confirmed identity. Use name only when status
is Known. Keep tracker IDs separate from names.

Invalid, missing, or multi-face inputs raise ValueError.
Missing model files raise FileNotFoundError.
The integration layer must handle these failures separately from Unknown.

Create one processor per processing worker. Its detector input size
changes per image; do not share it across concurrent calls.

## Current limitations

- One reference embedding per person.
- Names currently act as keys; identical names cannot be enrolled twice.
- Similarity threshold 0.40 and ambiguity margin 0.05 are provisional.
- Only a small demonstration has been performed; accuracy is not validated.
- Identical twins may remain indistinguishable.
- No liveness detection or protection against photo/replay attacks.
- No explicit blur, minimum-face-size, or pose quality gate yet.
- Gallery JSON is plaintext and must be kept private.
- Replacing a gallery object requires rebuilding the recognition service.

## Privacy and GitHub

Enroll only consenting participants.
Do not commit photos, embeddings, gallery JSON, credentials or weights.

Copy the package's ignore rules into the main repository's root
.gitignore as well, so models/ and private_data/ are covered.

Notebook outputs can contain face photos and biometric data.
Do not publish the development notebook without clearing and reviewing it.
