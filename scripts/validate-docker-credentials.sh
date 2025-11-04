#!/bin/bash

# Script to validate Docker Hub credentials
# Usage: ./scripts/validate-docker-credentials.sh <docker_username> <docker_password>

set -e

DOCKER_USER=${1:-""}
DOCKER_PASS=${2:-""}

if [ -z "$DOCKER_USER" ] || [ -z "$DOCKER_PASS" ]; then
    echo "Usage: $0 <docker_username> <docker_password>"
    echo "Please provide Docker Hub username and password"
    exit 1
fi

echo "Validating Docker Hub credentials for user: $DOCKER_USER"

# Test Docker login
echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
LOGIN_STATUS=$?

if [ $LOGIN_STATUS -eq 0 ]; then
    echo "SUCCESS: Docker Hub credentials are valid"
    docker logout
else
    echo "ERROR: Docker Hub credentials are invalid (exit code: $LOGIN_STATUS)"
    exit 1
fi