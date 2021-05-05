This is a package for supporting pyppeteer in Scrapy, also this package is a module
in [GerapyPyppeteer](https://github.com/Gerapy/GerapyPyppeteer)

# 在原来基础上增加 page.click，以及代理的用户名和密码验证

```python
def start_requests(self):
    for page in range(1, 2):
        yield PyppeteerRequest(self.base_url, callback=self.parse_index, dont_filter=True,
                               wait_for=".vjs-poster",
                               click="xpath",
                               proxy="http://username:password@ip:prot")


```

```重定向解决办法，直接在原来页面点击，增加wait_for_next，验证下一面是否成功进入
def start_requests(self):
    yield PyppeteerRequest(
        url="https://www.d2pass.com/search?k=%E7%B9%B0%E3%82%8A%E8%BF%94%E3%81%97%E6%BF%83%E5%8E%9A%E3%81%AA%E3%81%AE%E3%82%92%E6%AC%B2%E3%81%97%E3%81%A6%E3%82%84%E3%81%BE%E3%81%AA%E3%81%84%E7%BE%8E%E3%83%9C%E3%83%87%E3%82%A3%E3%83%95%E3%83%BC%E3%83%89%E3%83%AB",
        wait_for=".gridimg", click=(
            "//*[@id='portfolio']/li/div/p[5]/a"), wait_for_next="#review-section",
        callback=self.parse)

```

# ScrapyPyppeteer

scrapy的一个下载中间件，无缝对接yppeteer

# handle await错误提示

在setting增加

```
AROAY_ENABLE_REQUEST_INTERCEPTION = False
```

# ScrapyPyppeteer

scrapy的一个下载中间件，无缝对接yppeteer

# 安装

pip3 install daoke-pyppeteer

```python
DOWNLOADER_MIDDLEWARES = {
    'aroay_pyppeteer.downloadermiddlewares.PyppeteerMiddleware': 543,
}
```

# 配置

```python
CONCURRENT_REQUESTS = 3
AROAY_PYPPETEER_PRETEND = False  # 默认为True,某些网站能检测无头或者webdriver驱动，需要开启
AROAY_PYPPETEER_HEADLESS = False  # 默认为True
AROAY_PYPPETEER_DOWNLOAD_TIMEOUT = 30  # 默认渲染页面超时时间30s

拦截请求
AROAY_PYPPETEER_IGNORE_RESOURCE_TYPES = ['stylesheet', 'script']
```

所有可选资源类型列表：

- document: the Original HTML document
- stylesheet: CSS files
- script: JavaScript files
- image: Images
- media: Media files such as audios or videos
- font: Fonts files
- texttrack: Text Track files
- xhr: Ajax Requests
- fetch: Fetch Requests
- eventsource: Event Source
- websocket: Websocket
- manifest: Manifest files
- other: Other files