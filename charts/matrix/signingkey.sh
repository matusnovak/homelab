#!/usr/bin/env bash

set -e

TMP_DIR=$(mktemp -d)
echo "TMP_DIR: ${TMP_DIR}"
docker run --rm -v ${TMP_DIR}:/data -e SYNAPSE_SERVER_NAME=${DOMAIN} -e SYNAPSE_REPORT_STATS=no docker.io/matrixdotorg/synapse:latest generate > /dev/null
echo "----------------"
sudo cat ${TMP_DIR}/${DOMAIN}.signing.key
