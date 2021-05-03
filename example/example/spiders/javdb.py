import scrapy

from aroay_pyppeteer import PyppeteerRequest


class JavdbSpider(scrapy.Spider):
    name = 'javdb'
    allowed_domains = ['javdb.com']

    def start_requests(self):
        yield PyppeteerRequest("http://www.httpbin.org/ip",
                               callback=self.parse)

    def parse(self, response):
        print(response.text)
