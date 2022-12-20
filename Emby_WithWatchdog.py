#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from curses import resize_term
import os
import time
import sys
import re
import json
import logging
from unicodedata import name
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, LoggingEventHandler
import requests

logging.basicConfig(
    level=logging.INFO,
    filename='/home/watchdog.log',
    filemode='a+',
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# 填充电报机器人的token
TG_BOT_TOKEN = os.getenv('BOT_TOKEN')
# 填充电报频道 chat_id
TG_CHAT_ID = os.getenv('CHAT_ID')
# 填充tmdb api token
TMDB_API_TOKEN = os.getenv('TMDB_API')
# 填充Emby媒体库路径
EMBY_MEDIA_LIB_PATH = os.getenv('MEDIA_PATH')

# 文件名中需额外转义字符
ESCAPE_CHAR = [' ', '(', ')', '\'']
# 排除的文件
EXCLUDE_FILE = ['tvshow.nfo', 'season.nfo']


def post_movieInfo(media_dir):
    tmp_list = list(media_dir)
    i = 0
    le = len(tmp_list)
    while i < le:
        if tmp_list[i] in ESCAPE_CHAR:
            tmp_list.insert(i, '\\')
            le += 1
            i += 2
        else:
            i += 1
    media_dir = ''.join(tmp_list)
    print(media_dir)

    # 获取电影标题
    cmd = (
        "echo \"cat //movie/title/text()\" | xmllint --shell "
        + media_dir
        + " | sed '1d;$d'"
    )
    media_title = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print(media_title)
    # 获取发行年份
    cmd = "xmllint --xpath '//movie/year/text()' " + media_dir
    media_year = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print(media_year)
    # 获取电影类型
    cmd = (
        "echo \"cat //movie/genre/text()\" | xmllint --shell "
        + media_dir
        + " | sed '1d;$d'"
    )
    media_type = os.popen(cmd).read()
    reg = re.compile('\n -------\n')
    media_type = reg.sub('|', media_type)[0 : len(reg.sub('|', media_type)) - 1]
    print(media_type)
    # 获取内容简介
    cmd = (
        "echo \"cat //movie/plot/text()\" | xmllint --nocdata --shell "
        + media_dir
        + " | sed '1d;$d'"
    )
    media_intro = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print(media_intro)
    # 获取上映日期
    cmd = "xmllint --xpath '//movie/releasedate/text()' " + media_dir
    media_rel = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print(media_rel)
    # 获取tmdb id
    cmd = "xmllint --xpath '//movie/tmdbid/text()' " + media_dir
    media_tmdbid = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print(media_tmdbid)
    # 获取imdb id
    cmd = "xmllint --xpath '//movie/imdbid/text()' " + media_dir
    media_imdbid = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print(media_imdbid)
    # 获取评分
    cmd = "xmllint --xpath '//movie/rating/text()' " + media_dir
    media_rating = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print(media_rating)

    # 组装tg_bot的post主体
    caption = (
        '#影视更新\n\[电影]\n片名： *'
        + media_title
        + '* ('
        + media_year
        + ')\n类型： '
        + media_type
        + '\n评分： '
        + media_rating
        + '\n\n上映日期： '
        + media_rel
        + '\n\n内容简介： '
        + media_intro
        + '\n\n相关链接： [TMDB](https://www.themoviedb.org/movie/'
        + media_tmdbid
        + '?language=zh-CN) | [IMDB](https://www.imdb.com/title/'
        + media_imdbid
        + '$)\n'
    )
    print(caption)

    # 从tmdb获取电影封面
    tmdb_url = (
        "https://api.themoviedb.org/3/movie/"
        + media_tmdbid
        + "/images?api_key="
        + TMDB_API_TOKEN
    )
    res = requests.get(tmdb_url)
    img_num = len(res.json()['posters'])
    print(img_num)
    imgs = []
    for i in range(img_num):
        imgs.append(res.json()['posters'][i]['file_path'])
    print(imgs)
    index = 0
    while index < img_num:
        try:

            media_imgurl = "https://image.tmdb.org/t/p/w500" + imgs[index]

            post_data = {
                'method': 'sendPhoto',
                'chat_id': TG_CHAT_ID,
                'photo': media_imgurl,
                'caption': caption,
                'parse_mode': 'Markdown',
            }

            # doPost
            tg_url = 'https://api.telegram.org/bot' + TG_BOT_TOKEN + '/'
            res = requests.post(tg_url, json=post_data)
            res.raise_for_status()
            break
        except:
            index += 1
            print("err occur! try next...")
            continue
    if index == img_num:
        post_data = {
            'method': 'sendMessage',
            'chat_id': TG_CHAT_ID,
            'text': caption,
            'parse_mode': 'Markdown',
        }
        try:
            # doPost
            tg_url = 'https://api.telegram.org/bot' + TG_BOT_TOKEN + '/'
            res = requests.post(tg_url, json=post_data)
            res.raise_for_status()
        except:
            print("Err!!!!!!!! plz check!!!!!!!!!!")


def post_episodesInfo(media_dir):
    tmp_list = list(media_dir)
    i = 0
    le = len(tmp_list)
    while i < le:
        if tmp_list[i] in ESCAPE_CHAR:
            tmp_list.insert(i, '\\')
            le += 1
            i += 2
        else:
            i += 1
    media_dir = ''.join(tmp_list)
    print(media_dir)
    # 先从剧集nfo文件中提取当前的season和episode
    cmd = "xmllint --xpath '//episodedetails/season/text()' " + media_dir
    media_season = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    cmd = "xmllint --xpath '//episodedetails/episode/text()' " + media_dir
    media_episode = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print('第' + media_season + '季|第' + media_episode + '集')
    # 获取剧集id
    media_dir = media_dir[0 : media_dir.find('Season')]
    # print(media_dir)
    media_dir += 'tvshow.nfo'
    # 发行年份
    cmd = "xmllint --xpath '//tvshow/year/text()' " + media_dir
    media_year = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    # 剧集imdb id
    cmd = "xmllint --xpath '//tvshow/imdb_id/text()' " + media_dir
    media_imdbid = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    # 剧集tmdb id
    cmd = "xmllint --xpath '//tvshow/tmdbid/text()' " + media_dir
    media_tmdbid = os.popen(cmd).read()[0 : len(os.popen(cmd).read()) - 1]
    print('tmdb_id: ' + media_tmdbid)
    # 获取剧集details
    tmdb_url = (
        'https://api.themoviedb.org/3/tv/'
        + media_tmdbid
        + '?api_key='
        + TMDB_API_TOKEN
        + '&language=zh-CN'
    )
    res_tmdb = requests.get(tmdb_url)
    res_tmdb.encoding = 'utf-8'
    # print(res_tmdb.json())
    # 获取 剧集标题
    media_title = res_tmdb.json()['name']
    print(media_title)
    # 获取剧集类型
    media_genres = ''
    for i in range(len(res_tmdb.json()['genres'])):
        if 10765 == res_tmdb.json()['genres'][i]['id']:
            continue
        else:
            media_genres = (
                media_genres + res_tmdb.json()['genres'][i]['name'] + '|'
            )
    media_genres = media_genres[0 : len(media_genres) - 1]
    print(media_genres)
    # 获取评分
    media_rating = res_tmdb.json()['vote_average']
    print(media_rating)

    # 从tmdb获取剧集封面
    media_imgurl = (
        "https://image.tmdb.org/t/p/w500" + res_tmdb.json()['poster_path']
    )
    print(media_imgurl)

    # 获取当前集信息
    tmdb_url = (
        'https://api.themoviedb.org/3/tv/'
        + media_tmdbid
        + '/season/'
        + media_season
        + '/episode/'
        + media_episode
        + '?api_key='
        + TMDB_API_TOKEN
        + '&language=zh-CN'
    )
    print(tmdb_url)
    res_tmdb = requests.get(tmdb_url)
    res_tmdb.encoding = 'utf-8'
    # print(res_tmdb.json())

    # 获取 season id + episodes id
    media_epinfo = (
        '第'
        + media_season
        + '季 | 第'
        + media_episode
        + '集  '
        + res_tmdb.json()['name']
    )
    print(media_epinfo)
    # 获取发布日期
    media_airDate = res_tmdb.json()['air_date']
    print(media_airDate)
    # 获取内容简介
    media_intro = res_tmdb.json()['overview']
    print(media_intro)

    # 组装tg_bot的post主体
    caption = (
        '#影视更新\n\[剧集]\n片名： *'
        + media_title
        + '* ('
        + media_year
        + ')\n剧集： '
        + media_epinfo
        + '\n类型： '
        + media_genres
        + '\n评分： '
        + str(media_rating)
        + '\n\n发布日期： '
        + str(media_airDate or 'no release date')
        + '\n\n内容简介： '
        + media_intro
        + '\n\n相关链接： [TMDB](https://www.themoviedb.org/tv/'
        + media_tmdbid
        + '?language=zh-CN) | [IMDB](https://www.imdb.com/title/'
        + media_imdbid
        + ')\n'
    )
    print(caption)
    post_data = {
        'method': 'sendPhoto',
        'chat_id': TG_CHAT_ID,
        'photo': media_imgurl,
        'caption': caption,
        "parse_mode": "Markdown",
    }
    # doPost
    tg_url = 'https://api.telegram.org/bot' + TG_BOT_TOKEN + '/'
    res = requests.post(tg_url, json=post_data)


class LogHandler(LoggingEventHandler):
    def on_created(self, event):
        path = event.src_path
        if event.is_directory:
            pass
        else:
            logging.info(path + "文件新增")

    def on_modified(self, event):
        pass


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        path = event.src_path
        file_name = os.path.basename(path)
        if file_name.endswith("nfo") and path.find('movie') > 0:
            post_movieInfo(path)
        elif (
            file_name.endswith("nfo")
            and path.find('episode') > 0
            and path.find('recycle') < 0
            and path.find('eaDir') < 0
            and file_name not in EXCLUDE_FILE
        ):
            post_episodesInfo(path)
        else:
            pass

        print(event)


if __name__ == '__main__':
    event_handler = MyHandler()
    observer = Observer()
    watch = observer.schedule(
        event_handler, path=EMBY_MEDIA_LIB_PATH, recursive=True
    )

    log_handler = LogHandler()
    observer.add_handler_for_watch(log_handler, watch)  # 写入日志
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
