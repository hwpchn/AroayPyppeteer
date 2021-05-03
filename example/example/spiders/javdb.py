import scrapy

from aroay_pyppeteer import PyppeteerRequest


class JavdbSpider(scrapy.Spider):
    name = 'javdb'
    allowed_domains = ['javdb.com']

    def start_requests(self):
        yield PyppeteerRequest("http://www.httpbin.org/ip",
                               callback=self.parse,
                               proxy="http://hwplargespeedproxies:EwftFeTD4QF4k0sZ@3.224.197.3:31112")

    def parse(self, response):
        print(response.text)
