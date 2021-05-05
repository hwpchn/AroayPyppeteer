import scrapy

from aroay_pyppeteer import PyppeteerRequest


class JavdbSpider(scrapy.Spider):
    name = 'javdb'
    allowed_domains = ['d2pass.com']

    def start_requests(self):
        yield PyppeteerRequest(
            url="https://www.d2pass.com/search?k=%E7%B9%B0%E3%82%8A%E8%BF%94%E3%81%97%E6%BF%83%E5%8E%9A%E3%81%AA%E3%81%AE%E3%82%92%E6%AC%B2%E3%81%97%E3%81%A6%E3%82%84%E3%81%BE%E3%81%AA%E3%81%84%E7%BE%8E%E3%83%9C%E3%83%87%E3%82%A3%E3%83%95%E3%83%BC%E3%83%89%E3%83%AB",
            wait_for=".gridimg", click=(
                "//*[@id='portfolio']/li/div/p[5]/a"), wait_for_next="#review-section",
            callback=self.parse)

    def parse(self, response):
        print(response.text)
