#!/bin/bash

PUID=${PUID:=0}
PGID=${PGID:=0}
UMASK=${UMASK:=777}

chown -R ${PUID}:${PGID} \
    /src \
    /config

if [[ "$(stat -c '%u' /cache)" != "${PUID}" ]] || [[ "$(stat -c '%g' /cache)" != "${PGID}" ]]; then
    chown ${PUID}:${PGID} \
        /cache
fi
if [[ "$(stat -c '%u' /media)" != "${PUID}" ]] || [[ "$(stat -c '%g' /media)" != "${PGID}" ]]; then
    chown ${PUID}:${PGID} \
        /media
fi
if [[ "$(stat -c '%u' /downloads)" != "${PUID}" ]] || [[ "$(stat -c '%g' /downloads)" != "${PGID}" ]]; then
    chown ${PUID}:${PGID} \
        /downloads
fi

umask ${UMASK}

echo -e "PUID=${PUID}\nPGID=${PGID}\numask=${UMASK}"

su-exec ${PUID}:${PGID} uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml
