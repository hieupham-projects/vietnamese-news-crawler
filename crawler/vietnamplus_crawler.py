import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm

from crawler.crawler_arguments import CrawlerArguments

from .base_crawler import BaseCrawler


class VietnamPlusCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments) -> None:
        super().__init__(arguments)
        self.sitemap = "https://www.vietnamplus.vn/sitemap.xml"

    def generate_month_range(self):
        start_month, start_year = self.arguments.start_range.split("-")
        end_month, end_year = self.arguments.end_range.split("-")
        start_date = datetime(int(start_year), int(start_month), 1)
        end_date = datetime(int(end_year), int(end_month), 1)

        # Ensure start_date is earlier than end_date
        if start_date > end_date:
            raise ValueError("Start date must be earlier than end date")

        current_date = start_date
        month_range = []

        while current_date <= end_date:
            month_range.append(current_date)
            # Move to the first day of the next month
            current_date = datetime(
                current_date.year + (current_date.month // 12),
                ((current_date.month % 12) + 1),
                1,
            )

        return month_range

    def _crawl_urls(self) -> List[str]:
        logger.info("Start crawling urls")
        response = requests.get(self.sitemap)
        datetimes = self.generate_month_range()
        sitemaps = [
            f"https://www.vietnamplus.vn/sitemaps/news-{datetime.strftime(date, '%Y-%m')}.xml"
            for date in datetimes
        ]
        urls = []

        for i in tqdm(range(len(sitemaps))):
            sitemap = sitemaps[i]
            if (
                sitemap != "https://www.vietnamplus.vn/sitemaps/categories.xml"
                and sitemap != "https://www.vietnamplus.vn/sitemaps/topics.xml"
            ):
                response = requests.get(sitemap)
                if response.status_code == 200:
                    xml_tree = ET.fromstring(requests.get(sitemap).content)
                    for url in xml_tree.findall(
                        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"
                    ):
                        urls.append(
                            url.find(
                                "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                            ).text
                        )
        return urls

    def _crawl_articles(self, url: Optional[str]) -> Optional[str]:
        if url != "https://www.vietnamplus.vn":
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "lxml")
                breadcrumb = soup.find("div", class_="breadcrumb breadcrumb-detail")
                h2_tag = breadcrumb.find("h2")
                category = h2_tag.find("a").text.strip()
                title = soup.find("h1", class_="article__title cms-title").text.strip()
                author_tag = soup.find("span", class_="author cms-author")
                author = ""
                if author_tag:
                    author = author_tag.text.strip()

                content = "\n".join([tag.text.strip() for tag in soup.find_all("p")])
                redundant = "Cơ quan chủ quản: THÔNG TẤN XÃ VIỆT NAM\nTổng Biên tập: TRẦN TIẾN DUẨN\nPhó Tổng Biên tập: NGUYỄN THỊ TÁM, NGUYỄN HOÀNG NHẬT\nGiấy phép số: 1374/GP-BTTTT do Bộ Thông tin và Truyền thông cấp ngày 11/9/2008.\nQuảng cáo: Phó TBT Nguyễn Thị Tám: 093.5958688, Email: tamvna@gmail.com\nĐiện thoại: (024) 39411349 - (024) 39411348, Fax: (024) 39411348\nEmail: vietnamplus2008@gmail.com\n© Bản quyền thuộc về VietnamPlus, TTXVN. Cấm sao chép dưới mọi hình thức nếu không có sự chấp thuận bằng văn bản."

                if content == redundant:
                    content = soup.find("div", attrs={"align": "justify"}).text.strip()
                    content = content.replace("   ", "\n")
                else:
                    content = "\n".join(
                        [tag.text.strip() for tag in soup.find_all("p")]
                    )
                    content = content.replace(redundant, "")

                return {
                    "title": title,
                    "author": author,
                    "category": category,
                    "content": content,
                }
            except Exception as e:
                logger.debug(f"Error {e} at {url}")
