# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from navermusic import NaverMusicCrawl

# Chrome-driver Setting
Chrome_driver = "./chromedriver/chromedriver.exe"
driver = webdriver.Chrome(Chrome_driver)
base = "http://www.instiz.net/iframe_ichart_score.htm?week=1"
driver.get(base)
week = driver.find_element_by_tag_name("select")
values = week.find_elements_by_xpath("//option[@value]")
value_list = np.array([value.get_attribute("value") for value in values])


# Convert the punctuation mark
def punctuation_convert(string):
    c_string = string
    if u'？' in string or u'！' in string:
        c_string = string.replace(u'！', u'!').replace(u'？', u'?')
    return c_string

df_index = ["Period", "Agency", "Release", "Album", "Song", "Artist", "Genre", "Label", "Lyric", "Composer",
            "Arrangement"]
result = pd.DataFrame(columns=df_index)

for v in value_list:
    agency = ""
    release = ""
    album_info = ['NaN'] * 8

    driver.get(base + "&selyear=" + v)
    driver.page_source.encode('utf-8')
    period = driver.find_element_by_xpath("//div[@class = 'ichart_score_title_right minitext3']").text
    path = "//div[@class = 'spage_intistore_body']//div[@class = 'spage_score_item_1st']"

    song_info = driver.find_element_by_xpath(path + "//div[@class = 'ichart_score_song']")
    artist_info = driver.find_element_by_xpath(path + "//div[@class = 'ichart_score_artist']")

    try:
        # First indexes : Release Date, Song title, Album title, Agency
        song_name = punctuation_convert(song_info.find_element_by_xpath("//div[@class = 'ichart_score_song1']//b").text)
        agency = artist_info.find_element_by_xpath("//div[@class = 'ichart_score_artist2']//span").text.strip()
        album = song_info.find_element_by_xpath("//div[@class = 'ichart_score_song2']//span//a").get_attribute("href")
        release_info = song_info.find_element_by_xpath("//div[@class = 'ichart_score_song2']//span").text
        release = re.compile("\([\d\.]+").search(release_info).group()[1:]

        # Second indexes : Genre, Lyric, composer, arrangement
        album_info = NaverMusicCrawl(album, song_name).info_crawler()
        # third indexes : second place song's information and was number 1 in last week
    except NoSuchElementException:
        pass
    finally:
        no_1_song = pd.DataFrame(data=[[period, agency, release] + album_info], columns=df_index)
        result = pd.concat([result, no_1_song], ignore_index=True)

driver.quit()
result.to_csv("list.csv", encoding='utf-8')