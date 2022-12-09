#!/usr/bin/python3
# -*- coding: UTF-8 -*-
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import string, requests, os, logging, time
from xml.etree.ElementTree import Element
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, LoggingEventHandler

# 填充电报机器人的token
TG_BOT_URL = 'https://api.telegram.org/bot%s/' % os.getenv('BOT_TOKEN')
# 填充电报频道 chat_id
TG_CHAT_ID = os.getenv('CHAT_ID')
# 填充tmdb api token
TMDB_API_TOKEN = os.getenv('TMDB_API')
# 填充Emby媒体库路径
EMBY_MEDIA_LIB_PATH = os.getenv('MEDIA_PATH')

EXCLUDE_FILE = ['tvshow.nfo', 'season.nfo']

logging.basicConfig(
    level=logging.INFO,
    filename='/home/watchdog.log',
    filemode='a+',
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class POST_ERR(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Media:
    def __init__(self, path: string, type: string) -> None:
        self.m_path = path
        self.m_type = type
        self.m_genre = ''
        self.m_tmdbid = ''
        self.m_imdbid = ''
        self.m_caption = (
            '#影视更新\n'
            + '\[{type_ch}]\n'
            + '片名： *{title}* ({year})\n'
            + '{episode}'
            + '类型： {genre}\n'
            + '评分： {rating}\n\n'
            + '上映日期： {rel}\n\n'
            + '内容简介： {intro}\n\n'
            + '相关链接： [TMDB](https://www.themoviedb.org/movie/{type}?language=zh-CN) | [IMDB](https://www.imdb.com/title/{imdbid}$)\n'
        )

    def m_PraseNfo(self) -> None:
        print('this is a parent prasing functiong')

    def m_post2Bot(self, imgUrl: list) -> None:
        for i, val in enumerate(imgUrl):
            try:
                media_poster_url = 'https://image.tmdb.org/t/p/w500%s' % val
                post_data = {
                    'method': 'sendPhoto',
                    'chat_id': TG_CHAT_ID,
                    'photo': media_poster_url,
                    'caption': self.m_caption,
                    'parse_mode': 'Markdown',
                }
                res = requests.post(TG_BOT_URL, json=post_data)
                res.raise_for_status()
                break
            except:
                print("err occur! try again...")
                continue
        if res.status_code != requests.codes.ok:
            print(
                'media [%s] poster send failed...try send message...'
                % self.m_path
            )
            try:
                post_data = {
                    'method': 'sendMessage',
                    'chat_id': TG_CHAT_ID,
                    'text': self.m_caption,
                    'parse_mode': 'Markdown',
                }
                res = requests.post(TG_BOT_URL, json=post_data)
                res.raise_for_status()
            except:
                raise POST_ERR(
                    'ERR!!! Media [%s] post caption failed!!!!' % self.m_path
                )

    def m_printCaption(self) -> None:
        print(self.m_caption)


class Movie(Media):
    def __init__(self, path: string, type: string) -> None:
        super().__init__(path, type)

    def m_PraseNfo(self) -> None:
        tree = ET.ElementTree(file=self.m_path)
        root = tree.getroot()
        for child in root:
            match child.tag:
                case 'title':
                    self.m_caption = self.m_caption.replace(
                        '{title}', child.text
                    )
                case 'year':
                    self.m_caption = self.m_caption.replace(
                        '{year}', child.text
                    )
                case 'genre':
                    self.m_genre += child.text + '|'
                case 'rating':
                    self.m_caption = self.m_caption.replace(
                        '{rating}', child.text
                    )
                case 'releasedate':
                    self.m_caption = self.m_caption.replace('{rel}', child.text)
                case 'plot':
                    self.m_caption = self.m_caption.replace(
                        '{intro}', child.text
                    )
                case 'tmdbid':
                    self.m_caption = self.m_caption.replace(
                        '{tmdbid}', child.text
                    )
                    self.m_tmdbid = child.text
                case 'imdbid':
                    self.m_caption = self.m_caption.replace(
                        '{imdbid}', child.text
                    )
                case _:
                    continue
        if len(self.m_genre) - 1 > 0:
            self.m_genre = self.m_genre[0 : len(self.m_genre) - 1]
        self.m_caption = self.m_caption.replace('{genre}', self.m_genre)
        self.m_caption = self.m_caption.replace('{episode}', '')
        self.m_caption = self.m_caption.replace('{type_ch}', '电影')

    def m_getPosterImgUrlList(self) -> list:
        tmdb_url = 'https://api.themoviedb.org/3/movie/%s/images?api_key=%s' % (
            self.m_tmdbid,
            TMDB_API_TOKEN,
        )
        res = requests.get(tmdb_url)
        img_num = len(res.json()['posters'])
        imgUrls = []
        for i in range(img_num):
            imgUrls.append(res.json()['posters'][i]['file_path'])

        return imgUrls


class Episode(Media):
    def __init__(self, path: string, type: string) -> None:
        super().__init__(path, type)

    def m_PraseNfo(self) -> None:
        tree = ET.ElementTree(file=self.m_path)
        root = tree.getroot()
        for child in root:
            match child.tag:
                case 'season':
                    season = child.text
                case 'episode':
                    episode = child.text
                case _:
                    continue
        #
        tvshow_path = self.m_path[0 : self.m_path.find('Season')] + 'tvshow.nfo'
        tree = ET.ElementTree(file=tvshow_path)
        root = tree.getroot()
        for child in root:
            match child.tag:
                case 'year':
                    self.m_caption = self.m_caption.replace(
                        '{year}', child.text
                    )
                case 'tmdbid':
                    self.m_caption = self.m_caption.replace(
                        '{tmdbid}', child.text
                    )
                    self.m_tmdbid = child.text
                case 'imdb_id':
                    self.m_caption = self.m_caption.replace(
                        '{imdbid}', child.text
                    )
                case _:
                    continue

        # try get episode details
        tmdb_url = (
            'https://api.themoviedb.org/3/tv/%s?api_key=%s&language=zh-CN'
            % (
                self.m_tmdbid,
                TMDB_API_TOKEN,
            )
        )
        res_tmdb = requests.get(tmdb_url)
        res_tmdb.encoding = 'utf-8'
        self.m_caption = self.m_caption.replace('{type_ch}', '剧集')
        self.m_caption = self.m_caption.replace(
            '{title}', res_tmdb.json()['name']
        )
        for i in range(len(res_tmdb.json()['genres'])):
            if 10765 == res_tmdb.json()['genres'][i]['id']:
                self.m_genre = self.m_genre + '科幻|'
            else:
                self.m_genre = (
                    self.m_genre + res_tmdb.json()['genres'][i]['name'] + '|'
                )
        if len(self.m_genre) - 1 > 0:
            self.m_genre = self.m_genre[0 : len(self.m_genre) - 1]
        self.m_caption = self.m_caption.replace('{genre}', self.m_genre)
        self.m_caption = self.m_caption.replace(
            '{rating}', str(res_tmdb.json()['vote_average'])
        )
        # stored poster url
        self.m_posterUrl = [res_tmdb.json()['poster_path']]

        # try get current episode info
        tmdb_url = (
            'https://api.themoviedb.org/3/tv/%s/season/%s/episode/%s?api_key=%s&language=zh-CN'
            % (self.m_tmdbid, season, episode, TMDB_API_TOKEN)
        )
        res_tmdb = requests.get(tmdb_url)
        res_tmdb.encoding = 'utf-8'
        self.m_caption = self.m_caption.replace(
            '{episode}',
            '剧集：第%s季|第%s集 %s\n' % (season, episode, res_tmdb.json()['name']),
        )
        self.m_caption = self.m_caption.replace(
            '{rel}', res_tmdb.json()['air_date']
        )
        self.m_caption = self.m_caption.replace(
            '{intro}', res_tmdb.json()['overview']
        )

    def m_getPosterImgUrlList(self) -> list:
        return self.m_posterUrl


def MajorProcessOnCreate(path: string, type: string) -> None:
    if path[len(path) - 1] == '\n':
        path = path[0 : len(path) - 1]
    if 'movie' == type:
        mediaItem = Movie(path, type)
    elif 'episode' == type:
        mediaItem = Episode(path, type)
    mediaItem.m_PraseNfo()
    # mediaItem.m_printCaption()
    # mediaItem.m_post2Bot(mediaItem.m_getPosterImgUrlList())
    if type == 'movie':
        tmp_path = path[0 : path.rfind('/')]
        name = tmp_path[tmp_path.rfind('/') + 1 :]
    elif type == 'episode':
        tmp_path = path[0 : path.rfind('/')]
        tmp_path_x = tmp_path[0 : tmp_path.rfind('/')]
        name = tmp_path_x[tmp_path.rfind('/') + 1 :]
    try:
        mediaItem.m_post2Bot(mediaItem.m_getPosterImgUrlList())
    except POST_ERR as e:
        print('[ERR] %s' % name)
    print('[OK] %s' % name)


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
            MajorProcessOnCreate(path, 'movie')
        elif (
            file_name.endswith("nfo")
            and path.find('episode') > 0
            and path.find('recycle') < 0
            and path.find('eaDir') < 0
            and file_name not in EXCLUDE_FILE
        ):
            MajorProcessOnCreate(path, 'episode')
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
