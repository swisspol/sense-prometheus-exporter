#!/bin/bash
set -eux -o pipefail

TAG="swisspol/sense-exporter:latest"

docker build -t "$TAG" .
docker push "$TAG"
