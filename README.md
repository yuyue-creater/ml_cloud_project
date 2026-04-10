# ML Cloud Deployment: Container vs Serverless

A CMPT 756 project that trains an Iris classification model and deploys it to Google Cloud Platform using two approaches — **container-based** (Cloud Run) and **serverless** (Cloud Functions Gen2) — then compares their latency and cold-start behavior through load testing.

## Project Structure

| File | Description |
|---|---|
| `train_model.py` | Trains a Random Forest classifier on the Iris dataset and saves `model.pkl` |
| `app.py` | Flask API for the **container** deployment (Cloud Run) |
| `main.py` | Entry point for the **serverless** deployment (Cloud Functions) |
| `Dockerfile` | Container image definition for Cloud Run |
| `requirements.txt` | Python dependencies |
| `load_test.py` | Sequential + single-request load test with CLI options |
| `load_test_concurrent.py` | Concurrent load test with cold-start measurement |
| `notes.md` | Deployment commands and endpoint references |

## Setup

### Prerequisites

- Python 3.11
- Google Cloud SDK (`gcloud`)
- A GCP project with Cloud Run, Cloud Functions, Artifact Registry, and Cloud Storage enabled

### Install Dependencies

```bash
conda create -n ml_cloud_env python=3.11 -y
conda activate ml_cloud_env
pip install -r requirements.txt
```

### Train the Model

```bash
python train_model.py
```

This produces `model.pkl`.

## Deployment

### 1. Container-Based (Cloud Run)

Build and push the Docker image, then deploy:

```bash
gcloud run deploy iris-container-api \
  --image <YOUR_IMAGE_URI> \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 5 \
  --memory=512M \
  --cpu=1 \
  --port 8080
```

### 2. Serverless (Cloud Functions Gen2)

```bash
gcloud functions deploy iris-predict-fn \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --entry-point predict \
  --trigger-http \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=5 \
  --memory=512M \
  --cpu=1 \
  --source=.
```

## Usage

Send a prediction request to either endpoint:

```bash
curl -X POST "<ENDPOINT_URL>" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

## Load Testing

### Sequential / Single-Request Test

```bash
# Default: 1 cold-start request + 20 warm requests per endpoint
python load_test.py

# Cold-start only (no warm requests)
python load_test.py --requests 0

# Longer warm run
python load_test.py --requests 200 --workers 20
```

### Concurrent Test

```bash
python load_test_concurrent.py
```

Both scripts report:
- **Single Request Test** — first-request latency (cold start if the service was idle)
- **Summary / Concurrent Test** — average, max, and min latency over multiple requests

## Key Findings

| Scenario | Container (Cloud Run) | Serverless (Cloud Functions) |
|---|---|---|
| Cold start | ~0.48 s (warm, min-instances=1) | ~7.2 s (cold, min-instances=0) |
| Warm single request | ~0.21 s | ~0.21 s |
| Warm avg (20 req) | ~0.34–0.40 s | ~0.29–0.35 s |

- **Cold start** is the dominant difference: the serverless function incurs significant latency (~7 s) when scaling from zero, while the container stays warm.
- **Warm latency** is comparable between both approaches for this lightweight model.
- Under light concurrent load (20 requests), both deployments achieve 100% success rate with similar throughput.