#!/bin/bash

chown ${PUID}:${PGID} \
    /config \
    /cache \
    /media \
    /downloads

su-exec ${PUID}:${PGID} uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml