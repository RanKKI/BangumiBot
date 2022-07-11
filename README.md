# 自动追番
懒惰使科技进步，自动订阅某些网站的 RSS，并根据 RSS 的更新下载番剧，重命名扔进 jellyfin 的媒体库进行刮削，从而实现自动追番

项目想法来自 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi)，也贡献了一点代码，写了点测试用例和 `CI/CD`

但问题出在，提供的 Docker 无法在我的树莓派上跑，经过一些操作，原因可能是 32 位系统 + ARM 引起的

加上 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi) 与 qBittorrent 耦合性太强了，于是有重写的想法，其中文本正则处理的代码出自 [EstrellaXD/Auto_Bangumi/auto_bangumi/parser/analyser/raw_parser.py](https://github.com/EstrellaXD/Auto_Bangumi/blob/c9c2b28389aac6ac4d778cdc7de1a77ca024b97e/auto_bangumi/parser/analyser/raw_parser.py)。

## 下载器支持
 - Aria2
 - qBittorrent

## Feature
 - RSS
   - [蜜柑计划](https://mikanani.me/)
   - [动漫花园](https://dmhy.org/)
 - 去重
   - 已下载番剧不会重复下载
   - 优先下载清晰度高的资源

## TODO
 - Transmission 支持
 - 语言选择的优先级
 - Docker
 - 保种
 - RSS 配置
 - RSS 自定义过滤规则的配置
 - 更新提示（可以通过 iOS 的 bear）