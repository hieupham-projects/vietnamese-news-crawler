from dataclasses import dataclass


@dataclass
class CrawlerArguments:
    """Crawler arguments dataclass"""

    start_range: str
    end_range: str
    category: str
