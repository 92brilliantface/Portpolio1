# -*- coding: utf-8 -*-

import urllib2
import numpy as np
from bs4 import BeautifulSoup


class NaverMusicCrawl(object):
    def __init__(self, url, song_name):
        self.url = url
        self.song_name = song_name

    def page_load(self):
        page = urllib2.urlopen(self.url)
        soup = BeautifulSoup(page, 'html5lib')
        return soup.body

    # Crawling the information of track(s).
    def info_crawler(self):
        album = ""
        label = ""
        artist = ""
        title = ""
        genre = ""
        lyric = ""
        composer = ""
        arrange = ""

        page = self.page_load()

        try:
            album = page.find("div", attrs={"class": "info_txt"}).h2.text
        except AttributeError:
            return ['NaN'] * 8
        else:
            album_info = page.find("dl", attrs={"class": "desc"}).findAll("dd")
            try:
                genre = album_info[1].text.strip()
                label = album_info[3].text
            except IndexError:
                pass

        try:
            artist = page.find("dd", attrs={"class": "artist"}).a.text
        # If album type is Compilation album
        except AttributeError:
            try:
                song = page.find("tbody").findAll("tr")
                for tag in song:
                    content = tag.findAll("span", attrs={"class": "ellipsis"})
                    if not content:
                        pass
                    elif self.song_name[:5] == unicode(content[0].text[:5]):
                        artist = content[1].text.strip()
            except IndexError:
                artist = page.find("td", {"class", "_artist artist no_ell2"}).a.text + u" 외"

        track_list = page.find("ol", attrs={"class": "song_info_ol"})

        try:
            for track in track_list.findAll("li"):
                song_title = track.find("span", attrs={"class": "tit"}).text
                if self.song_name.upper() == song_title.upper() or \
                        (self.song_name[-2:] == '..' and self.song_name[:5].upper() in unicode(song_title.upper())):
                    title = song_title
                    prod = track.findAll("span", attrs={"class": "info"})
                    lyric = ','.join([name.text for name in prod[0].findAll("a")])
                    composer = ','.join([name.text for name in prod[1].findAll("a")])
                    arrange = ','.join([name.text for name in prod[2].findAll("a")])
        except AttributeError:
            print "정보 없음 - Can't Find Any Infomation"
            pass
        except IndexError:
            print "정보 없음 - Can't Find Any Infomation"
            pass
        finally:
            return [album, title, artist, genre, label, lyric, composer, arrange]

if __name__ == "__main__":
    nmc = NaverMusicCrawl("http://music.naver.com/album/index.nhn?albumId=648755",
                          u"Day Day (Feat. 박재범) (Prod. by..")
    print nmc.info_crawler()