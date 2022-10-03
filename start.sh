#!/bin/bash

chown ${PUID}:${PGID} \
    /config \
    /config/rss.json \
    /config/notification.json \
    /src/conf/log.yml \
    /cache \
    /media \
    /downloads

su-exec ${PUID}:${PGID} uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml