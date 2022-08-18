# Emby_WithWatchdog
## 修订版本
| 版本 | 日期 | 修订说明 |
| :----- | :----- | :----- |
| V0.000.4 | 2022.08.18 | <li>新增MovieTitleTranslate.py小工具，用于按照刮削后，将电影目录重命名为nfo文件中的<title>(<year>)，统一所有电影目录的明明风格; |
| V0.000.3 | 2022.06.10 | <li>bug修复，修复新增剧集时，"season.nfo"未排除导致解析异常的问题; |
| V0.000.2 | 2022.05.28 | <li>bug修复，修复当文件名中出现单引号时，无法正确解析的问题; |
| V0.000.1 | 2022.05.20 | <li>参数修改为从环境变量获取;<li>原剧集信息获取逻辑修改，修复因tmdb的tv/detail更新不及时，导致新入库剧集信息不匹配的问题 |
## 简介
借助python中的看门狗模块（“watchdog”）监视emby媒体库目录，通过电报（telegram）的bot和channel，向频道订阅者推送Emby媒体库中新增影片信息，包括电影和剧集。

该方法基于 Emby Server 自动影片刮削生成的“xxxx.nfo”文件。影片新入库后，Emby Server 自动执行刮削生成xml格式的nfo文件，通过xmllint可以解析到部分该影片或者剧集的信息。而封面图片等信息，则需要通过tmdb资料库的api token进行查询获取。因此需依赖python中的“requests”模块，通过调用"get"方法获取完整信息。在按照电报bot的api文档对payload数据行组装后，调用post方法推送给bot，由bot发布至对应频道。

## 环境依赖
1. python3
2. python Module: *watchdog*, *requests* (cmd: `pip3 install watchdog requests`)
3. xmllint (os: ubuntu 20.04，cmd: `sudo apt-get install libxml2-utils`)

## 参数说明
| 参数 | 说明 |
| -- | -- |
| TG_BOT_TOKEN | 电报 bot token |
| TG_CHAT_ID | 电报频道 chat_id |
| TMDB_API_TOKEN | TMDB api token |
| EMBY_MEDIA_LIB_PATH| Emby 媒体库路径 |

## 参考文档
+ tmdb api 文档：https://developers.themoviedb.org/3
+ telegram bot api 文档：https://core.telegram.org/bots/api
