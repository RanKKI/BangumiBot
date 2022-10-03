FROM python:3.10-alpine

WORKDIR /src

RUN apk add --no-cache \
    build-base \
    libxml2-dev \
    libxslt-dev \
    curl \
    su-exec \
    bash

# DO NOT EDIT
# USER NEEDS MOUNT TO THESE DIRECTORY
ENV BANGUMI_DOWNLOAD_FOLDER=/downloads \
    BANGUMI_MEDIA_FOLDER=/media \
    BANGUMI_CONFIG_PATH=/config \
    BANGUMI_CACHE_FOLDER=/cache

RUN pip install -r https://raw.githubusercontent.com/RanKKI/Bangumi/main/requirements.txt

RUN mkdir -p \
    /downloads \
    /media \
    /cache \
    /config

COPY --chmod=755 . .

# API PORT
EXPOSE 8000

CMD ["sh", "start.sh"]
