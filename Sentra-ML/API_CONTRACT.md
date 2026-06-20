# SENTRA-ML API Contract

Base URL for local development:

```text
http://127.0.0.1:8001
```

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

## Detect Image

Used by Backend to send an uploaded image or sampled CCTV frame to ML.

```http
POST /detect-image?camera_code=CAM-01
Content-Type: multipart/form-data
```

Form fields:

```text
file: image file
```

Response:

```json
{
  "camera_code": "CAM-01",
  "worker_count": 1,
  "detections": [
    {
      "worker_id": "W-001",
      "helmet": true,
      "vest": false,
      "in_danger_zone": false,
      "violations": ["NO_VEST"],
      "risk_score": 30,
      "risk_level": "WARNING",
      "box": [100, 120, 250, 500]
    }
  ],
  "summary": {
    "total_violation": 1,
    "highest_risk": "WARNING",
    "screenshot_saved": false,
    "screenshot_path": null
  }
}
```

Risk levels:

```text
SAFE, WARNING, HIGH, CRITICAL
```

Violation codes:

```text
NO_HELMET
NO_VEST
DANGER_ZONE_ENTRY
```

## Backend Integration Flow

Recommended hackathon flow:

```text
Frontend -> Backend -> SENTRA-ML -> Backend DB -> Frontend dashboard
```

Backend should store:

```text
camera_code
worker_count
detections
summary
timestamp
screenshot_path, if available
```

## Curl Example

```bash
curl -X POST "http://127.0.0.1:8001/detect-image?camera_code=CAM-01" \
  -F "file=@assets/sample4.jpeg"
```
