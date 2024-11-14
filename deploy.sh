#!/bin/zsh

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

gcloud run deploy attendance-management-backend \
  --image us-central1-docker.pkg.dev/attendance-management-0000/attendance-management/attendance-management-backend:v${VERSION} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --update-env-vars VERSION=${VERSION}