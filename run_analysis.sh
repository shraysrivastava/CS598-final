#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="nyc-weather-traffic-analysis-1"

echo "clearing out results/ directory..."
rm -rf results
mkdir -p results

echo "building docker image '${IMAGE_NAME}'..."
docker build -t "${IMAGE_NAME}" .

echo "running analysis inside Docker..."
docker run --rm \
  -v "$(pwd)/datasets:/app/datasets" \
  -v "$(pwd)/results:/app/results" \
  "${IMAGE_NAME}"

