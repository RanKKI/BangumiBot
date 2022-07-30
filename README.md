# 自动追番
[![Unittest](https://github.com/RanKKI/Bangumi/actions/workflows/test.yml/badge.svg)](https://github.com/RanKKI/Bangumi/actions/workflows/test.yml) [![Build](https://github.com/RanKKI/Bangumi/actions/workflows/docker.yml/badge.svg)](https://github.com/RanKKI/Bangumi/actions/workflows/docker.yml)

[English](./README.md) [中文](./README_ZH.md)

<img src="/images/img_1.jpg" width=30% /> <img src="/images/img_2.jpg" width=50% />

> The first app is the official Jellyfin iOS client [Swiftfin](https://github.com/jellyfin/Swiftfin) (Still under Testflight)，The second app [Bark](https://github.com/Finb/Bark) which allows sending notification to your iPhone by HTTP request

## Feature
 - RSS
   - [蜜柑计划](https://mikanani.me/)
   - [动漫花园](https://dmhy.org/)
   - Support extra Site plugins
   - Support Filter based on site or global
 - Deduplicate
   - Downloaded content
   - Resolution priority
 - Downloader
   - Aria2
   - qBittorrent
   - Transmission
 - Support seeding after completed

## How to use

 - Copy .env.example to .env
 - Setup the downloader config, i.e. type, username, password
 - Set redis IP, Port and password
 - Set scrape frequency
 - Copy ./config_example tp ./config
 - Edit [RSS](#rss) Config `./config/rss.json `
 - Edit [Notification](#notification) Config `./config/notification.json`
 - Install all required libs  `pip install -r requirements.txt`
 - Start service `uvicorn main:app --host 0.0.0.0 --log-config conf/log.yml`

## Docker

```
docker network create --subnet=10.1.0.0/16 bangumi_network

docker run --name redis -p 6379:6379 \
  --net bangumi_network \
  --ip 10.1.0.20 \
  -d redis

docker run -d \
  --name aria2 --restart unless-stopped --log-opt max-size=1m \
  --net bangumi_network \
  -e PUID=$UID -e PGID=$GID -e UMASK_SET=022 \
  -e RPC_PORT=6800 -p 6800:6800 \
  -e LISTEN_PORT=6888 \
  -e RPC_SECRET="bangumi_aria2" \
  -p 6888:6888 -p 6888:6888/udp \
  -v ${pwd}/.cache/aria2-config:/config \
  -v ${pwd}/.cache/aria2-downloads:/downloads \
  --ip 10.1.0.21 \
  p3terx/aria2-pro

docker run --name bangumi \
  -e BANGUMI_CHECK_INTERVAL=600 \
  -e BANGUMI_CLIENT_TYPE="aria2" \
  -e BANGUMI_CLIENT_IP="10.1.0.21" \
  -e BANGUMI_CLIENT_PORT="6800" \
  -e BANGUMI_CLIENT_USERNAME="" \
  -e BANGUMI_CLIENT_PASSWORD="bangumi_aria2" \
  -e BANGUMI_REDIS_HOST="10.1.0.20" \
  -e BANGUMI_REDIS_PORT="6379" \
  -e BANGUMI_REDIS_PASSWORD="" \
  --ip 10.1.0.22 \
  -p 8000:8000 \
  -v /media:/media \
  -v /downloads:/downloads \
  -v /config:/config \
  --net bangumi_network -d \
  rankki/bangumi:latest
```

### Docker Compose

> Noted，no Web UI for Aria2, you may use [ziahamza/webui-aria2](https://github.com/ziahamza/webui-aria2)

```
cd /docker/<downloader>/

cat << EOF > .env
DOWNLOAD_PATH=/arai2_downloads
BANGUMI_CONFIG=/bangumi_config
MEDIA_PATH=/media
DOWNLOAD_CONFIG=/bt_config
GID=${GID}
UID=${UID}
EOF

docker compose up
```

### Docker Proxy
```
environment:
  - HTTPS_PROXY=http://host.docker.internal:20173
  - HTTP_PROXY=http://host.docker.internal:20173
  - NO_PROXY=10.1.0.1/16, 192.168.1.1/16, *.localhost, *.local, 127.0.0.0/8, localhost
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Config
### Env
```
BANGUMI_LOGGER_LEVEL = "[INFO|DEBUG]"  # KEEP at INFO,
BANGUMI_SEEDING = [1|yes|true] # seeding after completed
```

### RSS
> Noted `rules`，**matched** items will be **filtered**。**NOT KEEP MATCHED ITEMS**
```
/config/rss.json
{
    "urls": [
      "https://mikanani.me/RSS/MyBangumi?token=<token>",
      {
        "url": "https://mikanani.me/RSS/MyBangumi?token=<token>",
        "rules": [
          "^filter_options" # filter for this site only
        ]
      }
    ],
    "rules": [ // filter for all of sites
      ".*ABC.*",
      "^FILTER_RULE"
    ],
    "parsers": [
        {
            "folder": "/path/to/plugins", # absolute path to the plugin, the folder must a Python Module with all plugin imported in the `__init__.py`
            "classes": [
                "your-parser-name", # the name of plugin class
                "another-parser-name"
            ]
        }
    ],
    "mapper": [ # remap the title to other, in case some titles are not recognized
      ["^\[ANi\] 即使如此依旧步步进逼（仅限港澳台地区） - (\d+) (\[.*\]\s*)+", "Soredemo Ayumu wa Yosetekuru - {} {}"]
    ]
}
```

### notification

all `url` callback will be called by `curl`

`script` must be a absolute path `/bin/bash /path/to/script.sh`, if you're using Docker, remember to mount the script folder to the container

the first parameter of the script will be the title of completed Anime. i.e. `/bin/bash /path/to/script.sh 'OVERLORD S02E03'`
```
/config/notification.json
[
    "https://api.day.app/<you-key-here>/AnimeUpdate/{title}", # http 通知
    {
      "url": "https://<some-url>/AnimeUpdate",
      "data": {
        "token": "xxxxxxx", # title will placed in <here>
      },
      "method": "<POST|GET>"
    }
    "/bin/script"
]
```

## FAQ
### Seeding
BANGUMI_SEEDING is not working in Docker due to some file system limitation

more details: [How to create hard link to file in a docker volume](https://stackoverflow.com/questions/55380443/how-to-create-hard-link-to-file-in-a-docker-volume)
