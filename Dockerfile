FROM python:3.10

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# NO NEED EDIT
ENV BANGUMI_CACHE_FOLDER = "/cache"

# DO NOT EDIT
# USER NEEDS MOUNT TO THESE DIRECTORY
ENV BANGUMI_DOWNLOAD_FOLDER = "/downloads"
ENV BANGUMI_MEDIA_FOLDER = "/media"
ENV BANGUMI_CONFIG_PATH = "/config"

# MAIN ENTRY
RUN echo "#!/bin/bash" > ./start.sh
RUN echo "exec python3 ./main.py &" >> ./start.sh
RUN echo "exec uvicorn bangumi:app --host 0.0.0.0 --log-config conf/log.yml" >> ./start.sh

# API PORT
EXPOSE 8000

CMD ["sh", "start.sh"]
