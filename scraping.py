from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import requests

# sparta@cluster0 (내 db폴더이름@내클러스터이름)
client = MongoClient('mongodb+srv://test:sparta@cluster0.m7jzf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://news.naver.com/main/ranking/popularDay.naver',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')


news = soup.select('#wrap > div.rankingnews._popularWelBase._persist > div.rankingnews_box_wrap._popularRanking > div > div > ul > li > div')

# title = news[1].select_one('a').text;
# time = news[1].select_one('span').text;
# print(title, time);
idNum = 0

# DB 날리기
db.news.drop()
for data in news:
    link = data.select_one('a')['href']
    title = data.select_one('a').text
    time = data.select_one('span').text
    # image = data.select_one('a img')['src']
    idNum += 1
    doc = {
        "id": idNum,
        "link": link,
        "title": title,
        "time": time,
        # "image": image
    }
    db.news.insert_one(doc)


