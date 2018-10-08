FROM python:3.6-alpine

COPY . /fs-server
WORKDIR /fs-server

VOLUME /data
