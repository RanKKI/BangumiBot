# 自动追番
懒惰使科技进步

项目想法来自 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi)，也贡献了一点代码，写了点测试用例和 `CI/CD`

但问题出在，提供的 Docker 无法在我的树莓派上跑，经过一些操作，原因可能是 32 位系统 + ARM 引起的

加上 [EstrellaXD/Auto_Bangumi](https://github.com/EstrellaXD/Auto_Bangumi) 与 qBittorrent 耦合性太强了，于是有重写的想法，其中文本正则处理的代码出自 [EstrellaXD/Auto_Bangumi/auto_bangumi/parser/analyser/raw_parser.py](https://github.com/EstrellaXD/Auto_Bangumi/blob/c9c2b28389aac6ac4d778cdc7de1a77ca024b97e/auto_bangumi/parser/analyser/raw_parser.py)。

## 下载器支持
 - Aria2
 - qBittorrent
 - ~~Transmission~~ (在做了)

## Feature
 - RSS
   - [蜜柑计划](https://mikanani.me/)
   - [动漫花园](https://dmhy.org/)
 - 去重
   - 已下载番剧不会重复下载
   - 优先下载清晰度高的资源
