#!/bin/bash

chown -R ${PUID}:${PGID} \
    /src

chown ${PUID}:${PGID} \
    /config \
    /config/rss.json \
    /config/notification.json \
    /cache \
    /media \
    /downloads

su-exec ${PUID}:${PGID} uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml