from typing import List

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm

from crawler.crawler_arguments import CrawlerArguments

from .base_crawler import BaseCrawler


class VietnamnetCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments) -> None:
        super().__init__(arguments)
        self.category = [
            "the-thao",
            "van-hoa",
            "giai-tri",
            "the-gioi",
            "doi-song",
            "kinh-doanh",
            "thoi-su",
            "chinh-tri",
            "giao-duc",
            "suc-khoe",
            "thong-tin-truyen-thong",
            "phap-luat",
            "bat-dong-san",
            "du-lich",
            "oto-xe-may",
        ]
        if self.arguments.category not in self.category:
            raise ValueError("Category not found")
        else:
            self.crawled_category = self.arguments.category

    def _crawl_urls(self) -> List[str]:
        logger.info("Start crawling urls")
        urls = []

        for i in tqdm(
            range(int(self.arguments.start_range), int(self.arguments.end_range))
        ):
            url = f"https://vietnamnet.vn/{self.crawled_category}-page{i}"
            try:
                reponse = requests.get(url)
                soup = BeautifulSoup(reponse.text, "lxml")
                title_news = soup.find_all(
                    "h3", class_="horizontalPost__main-title vnn-title title-bold"
                )
                for new in title_news:
                    if "https://vietnamnet.vn/" in url:
                        urls.append(f'{new.a["href"]}')
                    else:
                        urls.append(f'https://vietnamnet.vn/{new.a["href"]}')
            except Exception as e:
                logger.debug(f"Error {e} at {url}")
        return urls

    def _crawl_articles(self, urls: List[str]) -> List[str]:
        logger.info("Start crawling articles")
        articles = []
        for url in tqdm(urls):
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "lxml")
                breadcrumb = soup.find("div", class_="bread-crumb-detail sm-show-time")
                category = breadcrumb.find_all("li")[1].find("a").text.strip()
                title = soup.find("h1", class_="content-detail-title").text.strip()
                description = soup.find(
                    "h2", class_="content-detail-sapo sm-sapo-mb-0"
                ).text
                author_tag = soup.find("span", class_="name")
                content_tags = soup.find_all("p")
                if content_tags:
                    content = (
                        description
                        + "\n"
                        + "\n".join(
                            [
                                tag.text.strip()
                                for tag in content_tags
                                if len(tag.text.split()) > 0
                            ]
                        )
                    )
                else:
                    content = description

                if author_tag:
                    author = author_tag.find("a").text.strip()
                    content = content.replace(author, "")
                else:
                    author = ""

                content = content.replace("\nChủ đề:", "")
                articles.append(
                    {
                        "title": title,
                        "author": author,
                        "category": category,
                        "content": content,
                    }
                )
            except Exception as e:
                logger.debug(f"Error {e} at {url}")
        return articles
