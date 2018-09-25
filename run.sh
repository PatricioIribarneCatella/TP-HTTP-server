#!/bin/bash

FS_SCALE=$1 WORKERS=$2 FS_WORKERS=$3 CACHE_SIZE=$4 FS_URL=$5 docker-compose up --build --scale fs=$1

