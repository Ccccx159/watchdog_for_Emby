# Emby_WithWatchdog
## 修订版本

<mark><font color="red">v1.x版本后续将不再更新维护，如有需要请更新使用v2.x版本！！！</font></mark>

| 版本 | 日期 | 修订说明 |
| :----- | :----- | :----- |
| v2.000.3 | 2022.12.28 | <li>新增v2.x版本dockerfile，docker image已上传至hub.docker.com |
| v2.000.2 | 2022.12.27 | <li>V2源码优化log文件路径获取方式，修改为可支持配置log文件目录;<li>V2源码bug修复，在文件创建事件触发后，增加1s延时，修复由于文件创建后过快进入xml解析，导致解析xml失败，提示元素为0的错误 |
| v2.000.1 | 2022.12.20 | <li>新增V2版本，去除外部xmllint依赖，由ElementTree解析nfo文件;<li>bug修复，修复提前释放剧集存在air_date字段为None的情况下直接进行字符串的追加和替换导致的错误崩溃 |
| v1.000.7 | 2022.10.31 | <li>新增dockerfile，基于ubuntu基础镜像构建，已上传镜像"b1gfac3c4t/overwatch"至hub.docker.com |
| v1.000.6 | 2022.10.31 | <li>优化过滤条件，"movies"修改为"movie";"episodes"修改为"episode" |
| v1.000.5 | 2022.10.28 | <li>优化python编码风格，修改log文件存储目录 |
| v1.000.4 | 2022.08.18 | <li>新增MovieTitleTranslate.py小工具，用于按照刮削后，将电影目录重命名为nfo文件中的\<title\>(\<year\>)，统一所有电影目录的命名风格; |
| v1.000.3 | 2022.06.10 | <li>bug修复，修复新增剧集时，"season.nfo"未排除导致解析异常的问题; |
| v1.000.2 | 2022.05.28 | <li>bug修复，修复当文件名中出现单引号时，无法正确解析的问题; |
| v1.000.1 | 2022.05.20 | <li>参数修改为从环境变量获取;<li>原剧集信息获取逻辑修改，修复因tmdb的tv/detail更新不及时，导致新入库剧集信息不匹配的问题 |
## 简介

借助python中的看门狗模块（“watchdog”）监视emby媒体库目录，通过电报（telegram）的bot和channel，向频道订阅者推送Emby媒体库中新增影片信息，包括电影和剧集。

## 实现说明

v2.x版本中，删除了原始版本中的xmllint依赖，仅通过python完成所有功能实现。**因此在dockerfile中将基础镜像由`ubuntu:latest`变更为`python:alpine3.17`，拉取后镜像体积由231MB减小至69.5MB，体积减少约70%**。

**watchdog_for_Emby** 对 Emby Server 自动影片刮削生成的“xxxx.nfo”文件进行监控。影片新入库后，Emby Server 自动执行刮削生成xml格式的nfo文件，~~通过xmllint可以解析到部分该影片或者剧集的信息~~通过“ElementTree”模块解析nfo文件，获取当前影片的基本信息。而影片的封面图，和剧集的详细信息，则需要通过TMDB的api进行查询获取，通过调用"requests.get()"方法完成查询。在按照电报bot的api文档对payload数据组装后，调用"requests.post()"方法推送给bot，由bot发布至对应频道。

## 依赖项

1. python3.10及以上版本（v2.x版本中，使用了match..case..语法，仅在3.10及以上版本完成支持）
2. python Module: *watchdog*, *requests* (cmd: `pip3 install watchdog requests`)，*ElementTree*
3. ~~xmllint (os: ubuntu 20.04，cmd: `sudo apt-get install libxml2-utils`)~~ v2.x版本中已去除此依赖

## 环境变量设置

| 参数 | 说明 |
| -- | -- |
| BOT_TOKEN | 电报 bot token |
| CHAT_ID | 电报频道 chat_id |
| TMDB_API | TMDB api token |
| MEDIA_PATH | Emby 媒体库路径 |
| LOG_PATH | <可选>日志文件路径，默认为`/var/tmp/overwatch.log` |

## Docker Run

~~~shell
docker run -d --name=watchdog-emby --restart=unless-stopped \
  -v "your media lib's host path":"media lib's container path" \
  -e BOT_TOKEN="your telegram bot's token" \
  -e CHAT_ID="your telegram channle's chat_id" \
  -e TMDB_API="tmdb api token" \
  -e MEDIA_PATH="media lib's container path" \
  -e LOG_PATH="log's output path" \
  b1gfac3c4t/overwatch
  
~~~

## 参考文档

+ tmdb api 文档：https://developers.themoviedb.org/3
+ telegram bot api 文档：https://core.telegram.org/bots/api
