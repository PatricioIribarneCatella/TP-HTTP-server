#!/bin/bash

FS_SCALE=$1 WORKERS=$2 FS_WORKERS=$3 docker-compose up --build --scale fs=$1

