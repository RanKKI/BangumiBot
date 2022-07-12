# 自动追番
懒惰使科技进步，自动订阅某些网站的 RSS，并根据 RSS 的更新下载番剧，重命名扔进 jellyfin 的媒体库进行刮削，从而实现自动追番

项目想法来自 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi)，也贡献了一点代码，写了点测试用例和 `CI/CD`

但问题出在，提供的 Docker 无法在我的树莓派上跑，经过一些操作，原因可能是 32 位系统 + ARM 引起的

加上 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi) 与 qBittorrent 耦合性太强了，于是有重写的想法，其中文本正则处理的代码出自 [EstrellaXD/Auto_Bangumi/auto_bangumi/parser/analyser/raw_parser.py](https://github.com/EstrellaXD/Auto_Bangumi/blob/c9c2b28389aac6ac4d778cdc7de1a77ca024b97e/auto_bangumi/parser/analyser/raw_parser.py)。

## Feature
 - RSS
   - [蜜柑计划](https://mikanani.me/)
   - [动漫花园](https://dmhy.org/)
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
 - 复制文件夹 ./config 到 ./.config
 - 修改[订阅](#rss)配置文件 `./.config/rss.json `
 - 修改[通知](#通知)配置文件 `./.config/notification.json`

## 配置
### RSS
```
/config/rss.json
{
    "urls": [ // 订阅链接
      "https://mikanani.me/RSS/MyBangumi?token=<token>"
    ],
    "rules": [ // 关键词过滤，正则表达
      r".*繁体.*",
      r"^另一个过滤"
    ]
}

```
### 通知
```
/config/notification.json
[
    "https://api.day.app/<you-key-here>/番剧更新！/{title}", # http 通知
    "/bin/script {title}" # 脚本通知
]
```

## TODO
 - 语言选择的优先级
 - Docker
 - 保种
 - ~~更新提示~~
 - ~~Transmission 支持~~
 - ~~RSS 配置~~
 - ~~RSS 自定义过滤规则的配置~~