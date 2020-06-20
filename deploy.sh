#!/bin/bash

STACK="$1"

if [ $# -eq 0 ]; then
    echo "No arguments supplied"
    exit 1
fi

docker-compose -p homelab_${STACK} -f docker-compose.${STACK}.yml up --build -d
