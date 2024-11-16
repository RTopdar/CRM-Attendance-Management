#!/bin/zsh

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
sudo service docker start
docker build -t us-central1-docker.pkg.dev/attendance-management-0000/attendance-management/attendance-management-backend:v${VERSION} .