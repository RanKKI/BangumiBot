FROM python:3.10-alpine

WORKDIR /src

RUN apk add --no-cache build-base libxml2-dev libxslt-dev curl

# DO NOT EDIT
# USER NEEDS MOUNT TO THESE DIRECTORY
ENV BANGUMI_DOWNLOAD_FOLDER=/downloads \
    BANGUMI_MEDIA_FOLDER=/media \
    BANGUMI_CONFIG_PATH=/config \
    BANGUMI_CACHE_FOLDER=/cache

COPY . .

RUN pip install -r requirements.txt

# MAIN ENTRY
RUN echo "#!/bin/bash" > ./start.sh && \
    echo "exec uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml" >> ./start.sh

# API PORT
EXPOSE 8000

CMD ["sh", "start.sh"]
