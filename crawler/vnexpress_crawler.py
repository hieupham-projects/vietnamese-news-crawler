# This file contains the crawler for vnexpress.net
from typing import List

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .crawler_arguments import CrawlerArguments
import time
import requests

from tqdm import tqdm
from loguru import logger


class VnExpressCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments) -> None:
        super().__init__(arguments=arguments)
        self._domain = "https://vnexpress.net"
        self.categories = {
            "thoi-su": 1001005,
            "goc-nhin": 1003450,
            "doi-song": 1002966,
            "the-gioi": 1001002,
            "the-thao": 1002565,
            "phap-luat": 1001007,
            "giai-tri": 1002691,
            "giao-duc": 1003497,
            "khoa-hoc": 1001009,
            "xe": 1001006,
            "kinh-doanh": 1003159,
            "du-lich": 1003231,
            "so-hoa": 1002592,
            "gia-dinh": 1002966,
            "suc-khoe": 1003750,
        }
        logger.debug(self.arguments.category)
        self.crawled_category = self.categories[self.arguments.category]

    def generate_date_range(self) -> List[str]:
        start_day, start_month, start_year = self.arguments.start_range.split("/")
        end_day, end_month, end_year = self.arguments.end_range.split("/")

        # Convert the day, month, and year into integers
        start_day = int(start_day)
        start_month = int(start_month)
        start_year = int(start_year)
        end_day = int(end_day)
        end_month = int(end_month)
        end_year = int(end_year)

        # Create time tuples for the start and end dates
        start_time_tuple = (start_year, start_month, start_day, 0, 0, 0, 0, 0, 0)
        end_time_tuple = (end_year, end_month, end_day, 0, 0, 0, 0, 0, 0)

        start_unix_timestamp = time.mktime(start_time_tuple)
        end_unix_timestamp = time.mktime(end_time_tuple)

        unix_timestamps = []
        while start_unix_timestamp <= end_unix_timestamp:
            unix_timestamps.append(int(start_unix_timestamp))
            start_unix_timestamp += 86400

        return unix_timestamps

    def _crawl_urls(self) -> List[str]:
        logger.info("Start crawling urls")
        urls = []
        unix_timestamp_list = self.generate_date_range()
        for i in tqdm(range(len(unix_timestamp_list))):
            unix_timestamp = unix_timestamp_list[i]
            url = f"https://vnexpress.net/category/day/cateid/{self.crawled_category}/fromdate/{unix_timestamp}/todate/{unix_timestamp}"
            try:
                reponse = requests.get(url)
                soup = BeautifulSoup(reponse.text, "lxml")
                title_news = soup.find_all("h3", class_="title-news")

                for new in title_news:
                    urls.append(new.a["href"])
            except:
                logger.debug(f"Error at {url}")
        return urls

    def _crawl_articles(self, urls: List[str]) -> List[str]:
        logger.info("Start crawling articles")
        articles = []
        for i in tqdm(range(len(urls))):
            url = urls[i]
            try:
                reponse = requests.get(url)
                soup = BeautifulSoup(reponse.text, "lxml")
                breadcrumb = soup.find("ul", class_="breadcrumb")
                category = breadcrumb.find_all("li")[0].text.strip()
                title = soup.find("h1", class_="title-detail").text.strip()
                content_tags = soup.find_all("p", class_="Normal")
                content = [tag.text.strip() for tag in content_tags]
                author = content.pop(-1)
                content = "\n".join(content)
                item = {
                    "title": title,
                    "author": author,
                    "category": category,
                    "content": content,
                }
                articles.append(item)
            except Exception as e:
                logger.debug(f"{e} at {url}")

        return articles
