#!/bin/bash

FS=$1
SCALE="${FS#*=}"

URL=$5

if [ -z "$5" ]
  then
        URL="--urlfs=http_fs_"
fi

FS_SCALE=$SCALE WORKERS=$2 FS_WORKERS=$3 CACHE_SIZE=$4 FS_URL=$URL docker-compose up --build --scale fs=$SCALE


