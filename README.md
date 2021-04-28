

This is a package for supporting pyppeteer in Scrapy, also this package is a module
in [GerapyPyppeteer](https://github.com/Gerapy/GerapyPyppeteer)

# 在原来基础上增加 page.click，以及代理的用户名和密码验证

```python
def start_requests(self):
    for page in range(1, 2):
        yield PyppeteerRequest(self.base_url, callback=self.parse_index, dont_filter=True,
                               wait_for=".vjs-poster",
                               click=".vjs-big-play-button",
                               proxy="http://username:password@ip:prot")


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
AROAY_PYPPETEER_PRETEND = False #默认为True,某些网站能检测无头或者webdriver驱动，需要开启
AROAY_PYPPETEER_HEADLESS = False #默认为True
AROAY_PYPPETEER_DOWNLOAD_TIMEOUT = 30 #默认渲染页面超时时间30s

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