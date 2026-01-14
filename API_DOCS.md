# API Documentation

## Project AETHER REST API

FastAPI-based REST API for frontend integration.

### Starting the Server

```bash
python api_server.py
```

Server runs at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

---

## Endpoints

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "service": "Project AETHER API",
  "version": "1.0.0",
  "status": "running"
}
```

---

### `POST /analyze`
Submit a report for analysis.

**Request Body:**
```json
{
  "report_text": "Your report text here..."
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "message": "Analysis started. Use /status/{job_id} to check progress."
}
```

**Status Codes:**
- `200`: Successfully queued
- `400`: Invalid report (too short)

---

### `GET /status/{job_id}`
Check the status of an analysis job.

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "running",
  "progress": "Processing factor 2/5: Market Feasibility",
  "current_factor": 2,
  "total_factors": 5,
  "result": null,
  "error": null
}
```

**Status Values:**
- `queued`: Waiting to start
- `running`: Currently processing
- `completed`: Analysis finished
- `failed`: Error occurred

**When completed, result contains:**
```json
{
  "result": {
    "final_report": "Full markdown report...",
    "factors": [
      {
        "factor": "Factor name",
        "verdict": "Judge verdict...",
        "peer_reviews": {...}
      }
    ],
    "report_path": "outputs/final_report_uuid.md",
    "reviews_path": "outputs/peer_review_uuid.json"
  }
}
```

---

### `GET /jobs`
List all analysis jobs.

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "uuid-1",
      "status": "completed",
      "created_at": "2026-01-14T10:30:00",
      "progress": "Analysis complete"
    },
    {
      "job_id": "uuid-2",
      "status": "running",
      "created_at": "2026-01-14T11:00:00",
      "progress": "Processing factor 1/3"
    }
  ]
}
```

---

### `DELETE /job/{job_id}`
Delete an analysis job from memory.

**Response:**
```json
{
  "message": "Job deleted successfully"
}
```

---

## Example Usage

### Using cURL

**Submit analysis:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "report_text": "We are considering launching a new AI-powered personal finance assistant app..."
  }'
```

**Check status:**
```bash
curl http://localhost:8000/status/YOUR_JOB_ID
```

### Using JavaScript/Fetch

```javascript
// Submit analysis
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    report_text: 'Your report text here...'
  })
});

const data = await response.json();
const jobId = data.job_id;

// Poll for status
const checkStatus = async () => {
  const statusResponse = await fetch(`http://localhost:8000/status/${jobId}`);
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    console.log('Analysis complete!', status.result);
  } else if (status.status === 'failed') {
    console.error('Analysis failed:', status.error);
  } else {
    console.log('Progress:', status.progress);
    setTimeout(checkStatus, 5000); // Check again in 5 seconds
  }
};

checkStatus();
```

### Using Python

```python
import requests
import time

# Submit analysis
response = requests.post('http://localhost:8000/analyze', json={
    'report_text': 'Your report text here...'
})

job_id = response.json()['job_id']

# Poll for completion
while True:
    status_response = requests.get(f'http://localhost:8000/status/{job_id}')
    status = status_response.json()
    
    print(f"Status: {status['status']} - {status['progress']}")
    
    if status['status'] == 'completed':
        print("Final Report:", status['result']['final_report'])
        break
    elif status['status'] == 'failed':
        print("Error:", status['error'])
        break
    
    time.sleep(5)
```

---

## CORS

CORS is enabled for all origins (`*`) by default. For production, configure specific origins in `api_server.py`.

---

## Notes

- Analysis runs as background task - doesn't block the API
- Job data stored in-memory - use a database for production
- Long-running analysis may take several minutes depending on factors
- API includes interactive documentation at `/docs` (Swagger UI)
