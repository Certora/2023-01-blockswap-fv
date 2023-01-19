#!/bin/sh

set -e

if [ -z "$1" -o -z "$2" ]; then
  echo "Usage: $0 USER_ID GROUP_ID" >&2
  echo "Build a docker image with a user with username 'docker' and password 'docker'." >&2
  echo "The user will be created with user id = USER_ID and group id = GROUP_ID." >&2
  echo "It is possible to pass the special value 'auto' for USER_ID and/or GROUP_ID." >&2
  echo "The special value 'auto' may be used instead of a user id or group id, in " >&2
  echo "which case the USER_ID/GROUP_ID will be detected automatically, with id command." >&2
  exit 1
fi

unset userid
unset groupid

if [ "$1" = auto ]; then
  userid=`id -u`
else
  userid=$1
fi

if [ "$2" = auto ]; then
  groupid=`id -g`
else
  groupid=$2
fi

dir=`dirname "$0"`

docker build -t 2023-01-blockswap-fv \
  --build-arg GROUP_ID="$groupid" \
  --build-arg USER_ID="$userid" \
  "$dir"
