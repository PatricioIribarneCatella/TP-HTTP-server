#!/bin/bash

FS_SCALE=$1 docker-compose up --build --scale fs=$1

