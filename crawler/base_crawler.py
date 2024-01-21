from abc import abstractmethod
from typing import Any, List

from .crawler_arguments import CrawlerArguments


class BaseCrawler(object):
    def __init__(self, arguments: CrawlerArguments) -> None:
        self.arguments = arguments

    def crawl_urls(self) -> List[str]:
        return self._crawl_urls()

    @abstractmethod
    def _crawl_urls(self) -> List[str]:
        pass

    def crawl_articles(self, urls: List[str]) -> List[str]:
        return self._crawl_articles(urls)

    @abstractmethod
    def _crawl_articles(self, urls: List[str]) -> List[str]:
        pass
