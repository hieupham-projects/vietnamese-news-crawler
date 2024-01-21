from .base_crawler import BaseCrawler
from .vnexpress_crawler import VnExpressCrawler
from .crawler_arguments import CrawlerArguments
from typing import Optional


class CrawlerFactory:
    @staticmethod
    def create_crawler(
        crawler_type: Optional[str],
        arguments: CrawlerArguments,
    ) -> BaseCrawler:
        crawler_dict = {"vnexpress": VnExpressCrawler(arguments=arguments)}
        if crawler_type in crawler_dict.keys():
            return crawler_dict[crawler_type]
        raise ValueError("Invalid crawler type")
