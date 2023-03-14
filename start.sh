#!/bin/bash

PUID=${PUID:=0}
PGID=${PGID:=0}
UMASK=${UMASK:=022}

chown -R ${PUID}:${PGID} \
    /src \
    /config

chown ${PUID}:${PGID} \
    /cache \
    /media \
    /downloads

umask ${UMASK}

echo -e "PUID=${PUID}\nPGID=${PGID}\nUmask=${UMASK}"

su-exec ${PUID}:${PGID} uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml
