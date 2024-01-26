from typing import Optional

from .base_crawler import BaseCrawler
from .crawler_arguments import CrawlerArguments
from .vietnamnet_crawler import VietnamnetCrawler
from .vietnamplus_crawler import VietnamPlusCrawler
from .vnexpress_crawler import VnExpressCrawler


class CrawlerFactory:
    @staticmethod
    def create_crawler(
        crawler_type: Optional[str],
        arguments: CrawlerArguments,
    ) -> BaseCrawler:
        crawler_dict = {
            "vnexpress": VnExpressCrawler(arguments=arguments),
            "vietnamnet": VietnamnetCrawler(arguments=arguments),
            "vietnamplus": VietnamPlusCrawler(arguments=arguments),
        }
        if crawler_type in crawler_dict.keys():
            return crawler_dict[crawler_type]
        raise ValueError("Invalid crawler type")
