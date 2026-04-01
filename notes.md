docker tag ml_cloud_project:latest \
  us-central1-docker.pkg.dev/project-adc921da-d084-48ca-bc9/iris-repo

BUCKET=cmpt756-iris-models-1774920381

IMAGE=us-central1-docker.pkg.dev/project-adc921da-d084-48ca-bc9/iris-repo/ml-cloud-project:latest

# deploy function:

gcloud functions deploy iris-predict-fn \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --entry-point predict \
  --trigger-http \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=5 \
  --concurrency=10 \
  --memory=512M \
  --cpu=1 \
  --source=. \
  --set-env-vars MODEL_BUCKET=cmpt756-iris-models-1774920381,MODEL_PATH=model.pkl

## run function testing:
FN_URL=$(gcloud functions describe iris-predict-fn \
  --gen2 --region us-central1 \
  --format='value(serviceConfig.uri)')
curl -X POST "$FN_URL" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'


# deploy api run:

  gcloud run deploy iris-container-api \
  --image us-central1-docker.pkg.dev/project-adc921da-d084-48ca-bc9/iris-repo/ml-cloud-project:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 5 \
  --concurrency=10 \
  --memory=512M \
  --cpu=1 \
  --port 8080 \
  --set-env-vars MODEL_BUCKET=cmpt756-iris-models-1774920381,MODEL_PATH=model.pkl

## api testing:

  URL_CONTAINER=$(gcloud run services describe iris-container-api \
  --platform managed --region us-central1 \
  --format='value(status.url)')
curl -X POST "$URL_CONTAINER/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'


api endpoint curl:

curl -X POST "https://iris-container-api-x76cce2eva-uc.a.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'

function endpoint curl:

curl -X POST "https://iris-predict-fn-x76cce2eva-uc.a.run.app" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'