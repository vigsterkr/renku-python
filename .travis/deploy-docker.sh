#!/usr/bin/env sh

docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD" $DOCKER_REGISTRY
docker build -t ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}minimal-notebook:latest .
docker push ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}minimal-notebook:latest