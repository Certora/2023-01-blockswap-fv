#!/bin/sh

set -e

if [ -z $1 ]; then
  echo "Usage: $0 REPO_PATH" >&2
  echo "The REPO_PATH is the local path to the 2023-01-blockswap-fv repository." >&2
  exit 1
fi

docker run --rm -it --name 2023-01-blockswap-fv \
  -v"$1":/home/docker/2023-01-blockswap-fv \
  2023-01-blockswap-fv:latest bash
