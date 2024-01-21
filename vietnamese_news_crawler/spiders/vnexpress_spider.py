import scrapy


class VnexpressSpiderSpider(scrapy.Spider):
    name = "vnexpress_spider"
    allowed_domains = ["vnexpress.net"]
    start_urls = ["https://vnexpress.net/"]

    def parse(self, response):
        pass
