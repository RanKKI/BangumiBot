# 自动追番
[![Unittest](https://github.com/RanKKI/Bangumi/actions/workflows/test.yml/badge.svg)](https://github.com/RanKKI/Bangumi/actions/workflows/test.yml) [![Build](https://github.com/RanKKI/Bangumi/actions/workflows/docker.yml/badge.svg)](https://github.com/RanKKI/Bangumi/actions/workflows/docker.yml)


懒惰使科技进步，自动订阅某些网站的 RSS，并根据 RSS 的更新下载番剧，重命名扔进 jellyfin 的媒体库进行刮削，从而实现自动追番

项目想法来自 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi)，也贡献了一点代码，写了点测试用例和 `CI/CD`

但问题出在，提供的 Docker 无法在我的树莓派上跑，经过一些操作，原因可能是 32 位系统 + ARM 引起的

加上 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi) 与 qBittorrent 耦合性太强了，于是有重写的想法，其中文本正则处理的代码出自 [EstrellaXD/Auto_Bangumi/auto_bangumi/parser/analyser/raw_parser.py](https://github.com/EstrellaXD/Auto_Bangumi/blob/c9c2b28389aac6ac4d778cdc7de1a77ca024b97e/auto_bangumi/parser/analyser/raw_parser.py)。

提供高自定义操作，可以自己写插件支持本项目不支持的 RSS 站点，甚至支持非 RSS 站点

[](./images/img_1.jpg)[](./images/img_2.jpg)

## Feature
 - RSS
   - [蜜柑计划](https://mikanani.me/)
   - [动漫花园](https://dmhy.org/)
   - 自定义插件
   - 自定义过滤（全局/站点）
 - 去重
   - 已下载番剧不会重复下载
   - 优先下载清晰度高的资源
 - 下载器
   - Aria2
   - qBittorrent
   - Transmission

## 使用指南

 - 复制 .env.example 到 .env
 - 设置下载器地址，用户名，密码
 - 设置 Redis 服务地址
 - 设置 RSS 更新频率
 - 复制文件夹 ./config_example 到 ./config
 - 修改[订阅](#rss)配置文件 `./config/rss.json `
 - 修改[通知](#通知)配置文件 `./config/notification.json`

## Docker

```
docker network create --subnet=10.1.0.0/16 bangumi_network # 建立一个网络

docker run --name redis -p 6379:6379 \
  --net bangumi_network \
  --ip 10.1.0.20 \
  -d redis # 启一个 Redis 实例并加入网络

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
  p3terx/aria2-pro # 启一个 Aria2 实例并加入网络

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

一键启动 Redis, Aria2 和本项目

注意，不带 Aria2 Web UI, 如果有需要可以使用 [ziahamza/webui-aria2](https://github.com/ziahamza/webui-aria2)

```
cat << EOF > .env
DOWNLOAD_PATH=/arai2_downloads
BANGUMI_CONFIG=/bangumi_config
MEDIA_PATH=/media
DOWNLOAD_CONFIG=/bt_config
GID=${GID}
UID=${UID}
EOF

cd /docker/<downloader>/ # 这里进入到你想使用的下载器的目录里

docker compose up
```

### Docker Proxy
因为众所周知的原因，可能需要加代理，可以在环境变量中添加
```
environment:
  - HTTPS_PROXY=http://host.docker.internal:20173
  - HTTP_PROXY=http://host.docker.internal:20173
  - NO_PROXY=10.1.0.1/16, 192.168.1.1/16, *.localhost, *.local, 127.0.0.0/8, localhost
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## 配置
### RSS
注意过滤的 `rules`，如果**命中**则会被**舍去**。**并非只下载命中资源**
```
/config/rss.json
{
    "urls": [ // 订阅链接
      "https://mikanani.me/RSS/MyBangumi?token=<token>",
      {
        "url": "https://mikanani.me/RSS/MyBangumi?token=<token>",
        "rules": [
          "^过滤选择" # 针对该站点单独过滤
        ]
      }
    ],
    "rules": [ // 关键词过滤，正则表达
      ".*繁体.*",
      "^另一个过滤"
    ],
    "parsers": [
        {
            "folder": "/path/to/plugins", # 插件的绝对路径，要求是一个 module，并 import 类到 `__init__.py`
            "classes": [
                "your-parser-name", # 插件类的名字
                "another-parser-name"
            ]
        }
    ]
}
```

### 通知
`url` 回调会使用 `curl` 调用，如果内置的无法满足需求，可以考虑使用脚本调用

脚本调用需要传入绝对路径，可以是 `/bin/bash /path/to/script.sh`。如果使用 Docker 容器方式运行本项目，需要将脚本目录挂在进容器，同时脚本目录是容器内的目录，并非本机目录。

脚本调用不需要像 `url` 一样加入 `{title}`。脚本第一个参数就是就是名字，比如配置 `/bin/bash /path/to/script.sh`，调用会执行 `/bin/bash /path/to/script.sh 'OVERLORD S02E03'`
```
/config/notification.json
[
    "https://api.day.app/<you-key-here>/番剧更新！/{title}", # http 通知
    {
      "url": "https://<some-url>/番剧更新！",
      "data": {
        "token": "xxxxxxx", # title 会放在 POST 请求的 body 里
      },
      "method": "<POST|GET>"
    }
    "/bin/script" # 脚本通知, 第一个参数为格式化后的名字
]
```

## TODO
 - 语言选择的优先级
 - 保种
 - ~~Docker~~
 - ~~更新提示~~
 - ~~Transmission 支持~~
 - ~~RSS 配置~~
 - ~~RSS 自定义过滤规则的配置~~