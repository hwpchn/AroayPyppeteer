import scrapy

from aroay_pyppeteer import PyppeteerRequest


class JavdbSpider(scrapy.Spider):
    name = 'javdb'
    allowed_domains = ['javdb.com']

    def start_requests(self):
        yield PyppeteerRequest("https://javdb.com/rankings/video_uncensored?period=daily",
                               callback=self.parse, cookies={"over18": "1"})

    def parse(self, response):
        print(response.text)
