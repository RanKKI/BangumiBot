#!/bin/bash

if [ ! -f "/config/notification.json" ]; then
    cp /src/config_example/notification.json /config/notification.json
fi

if [ ! -f "/config/rss.json" ]; then
    cp /src/config_example/rss.json /config/rss.json
fi

chown ${PUID}:${PGID} \
    /config \
    /config/rss.json \
    /config/notification.json \
    /src/conf/log.yml \
    /cache \
    /media \
    /downloads

su-exec ${PUID}:${PGID} uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml