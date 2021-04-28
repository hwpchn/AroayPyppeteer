import asyncio
import sys
import urllib.parse
from io import BytesIO

import twisted.internet
from pyppeteer import launch
from pyppeteer.errors import PageError, TimeoutError
from scrapy.http import HtmlResponse
from scrapy.utils.python import global_object_name
from twisted.internet.asyncioreactor import AsyncioSelectorReactor
from twisted.internet.defer import Deferred

from .pretend import SCRIPTS as PRETEND_SCRIPTS
from .settings import *

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

reactor = AsyncioSelectorReactor(asyncio.get_event_loop())

# install AsyncioSelectorReactor
twisted.internet.reactor = reactor
sys.modules['twisted.internet.reactor'] = reactor


def as_deferred(f):
    """
    transform a Twisted Deffered to an Asyncio Future
    :param f: async function
    """
    return Deferred.fromFuture(asyncio.ensure_future(f))


logger = logging.getLogger('daoke.daoke_pyppeteer')


class PyppeteerMiddleware(object):
    """
    Downloader middleware handling the requests with Puppeteer
    """

    def _retry(self, request, reason, spider):
        """
        get retry request
        :param request:
        :param reason:
        :param spider:
        :return:
        """
        if not self.retry_enabled:
            return

        retries = request.meta.get('retry_times', 0) + 1
        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.error("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})

    @classmethod
    def from_crawler(cls, crawler):
        """
        init the middleware
        :param crawler:
        :return:
        """
        settings = crawler.settings
        logging_level = settings.get('DAOKE_PYPPETEER_LOGGING_LEVEL', DAOKE_PYPPETEER_LOGGING_LEVEL)
        logging.getLogger('websockets').setLevel(logging_level)
        logging.getLogger('daoke_pyppeteer').setLevel(logging_level)

        # init settings
        cls.window_width = settings.get('DAOKE_PYPPETEER_WINDOW_WIDTH', DAOKE_PYPPETEER_WINDOW_WIDTH)
        cls.window_height = settings.get('DAOKE_PYPPETEER_WINDOW_HEIGHT', DAOKE_PYPPETEER_WINDOW_HEIGHT)
        cls.default_user_agent = settings.get('DAOKE_PYPPETEER_DEFAULT_USER_AGENT',
                                              DAOKE_PYPPETEER_DEFAULT_USER_AGENT)
        cls.headless = settings.get('DAOKE_PYPPETEER_HEADLESS', DAOKE_PYPPETEER_HEADLESS)
        cls.dumpio = settings.get('DAOKE_PYPPETEER_DUMPIO', DAOKE_PYPPETEER_DUMPIO)
        cls.ignore_https_errors = settings.get('DAOKE_PYPPETEER_IGNORE_HTTPS_ERRORS',
                                               DAOKE_PYPPETEER_IGNORE_HTTPS_ERRORS)
        cls.slow_mo = settings.get('DAOKE_PYPPETEER_SLOW_MO', DAOKE_PYPPETEER_SLOW_MO)
        cls.ignore_default_args = settings.get('DAOKE_PYPPETEER_IGNORE_DEFAULT_ARGS',
                                               DAOKE_PYPPETEER_IGNORE_DEFAULT_ARGS)
        cls.handle_sigint = settings.get('DAOKE_PYPPETEER_HANDLE_SIGINT', DAOKE_PYPPETEER_HANDLE_SIGINT)
        cls.handle_sigterm = settings.get('DAOKE_PYPPETEER_HANDLE_SIGTERM', DAOKE_PYPPETEER_HANDLE_SIGTERM)
        cls.handle_sighup = settings.get('DAOKE_PYPPETEER_HANDLE_SIGHUP', DAOKE_PYPPETEER_HANDLE_SIGHUP)
        cls.auto_close = settings.get('DAOKE_PYPPETEER_AUTO_CLOSE', DAOKE_PYPPETEER_AUTO_CLOSE)
        cls.devtools = settings.get('DAOKE_PYPPETEER_DEVTOOLS', DAOKE_PYPPETEER_DEVTOOLS)
        cls.executable_path = settings.get('DAOKE_PYPPETEER_EXECUTABLE_PATH', DAOKE_PYPPETEER_EXECUTABLE_PATH)
        cls.disable_extensions = settings.get('DAOKE_PYPPETEER_DISABLE_EXTENSIONS',
                                              DAOKE_PYPPETEER_DISABLE_EXTENSIONS)
        cls.hide_scrollbars = settings.get('DAOKE_PYPPETEER_HIDE_SCROLLBARS', DAOKE_PYPPETEER_HIDE_SCROLLBARS)
        cls.mute_audio = settings.get('DAOKE_PYPPETEER_MUTE_AUDIO', DAOKE_PYPPETEER_MUTE_AUDIO)
        cls.no_sandbox = settings.get('DAOKE_PYPPETEER_NO_SANDBOX', DAOKE_PYPPETEER_NO_SANDBOX)
        cls.disable_setuid_sandbox = settings.get('DAOKE_PYPPETEER_DISABLE_SETUID_SANDBOX',
                                                  DAOKE_PYPPETEER_DISABLE_SETUID_SANDBOX)
        cls.disable_gpu = settings.get('DAOKE_PYPPETEER_DISABLE_GPU', DAOKE_PYPPETEER_DISABLE_GPU)
        cls.download_timeout = settings.get('DAOKE_PYPPETEER_DOWNLOAD_TIMEOUT',
                                            settings.get('DOWNLOAD_TIMEOUT', DAOKE_PYPPETEER_DOWNLOAD_TIMEOUT))
        cls.ignore_resource_types = settings.get('DAOKE_PYPPETEER_IGNORE_RESOURCE_TYPES',
                                                 DAOKE_PYPPETEER_IGNORE_RESOURCE_TYPES)
        cls.screenshot = settings.get('DAOKE_PYPPETEER_SCREENSHOT', DAOKE_PYPPETEER_SCREENSHOT)
        cls.pretend = settings.get('DAOKE_PYPPETEER_PRETEND', DAOKE_PYPPETEER_PRETEND)
        cls.sleep = settings.get('DAOKE_PYPPETEER_SLEEP', DAOKE_PYPPETEER_SLEEP)
        cls.enable_request_interception = settings.getbool('DAOKE_ENABLE_REQUEST_INTERCEPTION',
                                                           DAOKE_ENABLE_REQUEST_INTERCEPTION)
        cls.retry_enabled = settings.getbool('RETRY_ENABLED')
        cls.max_retry_times = settings.getint('RETRY_TIMES')
        cls.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        cls.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

        return cls()

    async def _process_request(self, request, spider):
        """
        use daoke_pyppeteer to process spider
        :param request:
        :param spider:
        :return:
        """
        # get daoke_pyppeteer meta
        pyppeteer_meta = request.meta.get('daoke_pyppeteer') or {}
        logger.debug('pyppeteer_meta %s', pyppeteer_meta)
        if not isinstance(pyppeteer_meta, dict) or len(pyppeteer_meta.keys()) == 0:
            return

        options = {
            'headless': self.headless,
            'dumpio': self.dumpio,
            'devtools': self.devtools,
            'args': [
                f'--window-size={self.window_width},{self.window_height}',
            ]
        }
        if self.executable_path:
            options['executablePath'] = self.executable_path
        if self.ignore_https_errors:
            options['ignoreHTTPSErrors'] = self.ignore_https_errors
        if self.slow_mo:
            options['slowMo'] = self.slow_mo
        if self.ignore_default_args:
            options['ignoreDefaultArgs'] = self.ignore_default_args
        if self.handle_sigint:
            options['handleSIGINT'] = self.handle_sigint
        if self.handle_sigterm:
            options['handleSIGTERM'] = self.handle_sigterm
        if self.handle_sighup:
            options['handleSIGHUP'] = self.handle_sighup
        if self.auto_close:
            options['autoClose'] = self.auto_close
        if self.disable_extensions:
            options['args'].append('--disable-extensions')
        if self.hide_scrollbars:
            options['args'].append('--hide-scrollbars')
        if self.mute_audio:
            options['args'].append('--mute-audio')
        if self.no_sandbox:
            options['args'].append('--no-sandbox')
        if self.disable_setuid_sandbox:
            options['args'].append('--disable-setuid-sandbox')
        if self.disable_gpu:
            options['args'].append('--disable-gpu')

        # pretend as normal browser
        _pretend = self.pretend  # get global pretend setting
        if pyppeteer_meta.get('pretend') is not None:
            _pretend = pyppeteer_meta.get('pretend')  # get local pretend setting to overwrite global
        if _pretend:
            options['ignoreDefaultArgs'] = [
                '--enable-automation'
            ]
            options['args'].append('--disable-blink-features=AutomationControlled')

        # set proxy
        _proxy = request.meta.get('proxy')
        if pyppeteer_meta.get('proxy') is not None:
            _proxy = pyppeteer_meta.get('proxy')
        if _proxy:
            # 如果有用户名和密码，则进行验证
            if "@" in str(_proxy):
                if str(_proxy).startswith("http://"):
                    self.username, self.password = str(_proxy).split("http://")[1].split("@")[0].split(":")
                    myproxy = "http://" + str(_proxy).split("http://")[1].split("@")[1]
                else:
                    self.username, self.password = str(_proxy).split("https://")[1].split("@")[0].split(":")
                    myproxy = "https://" + str(_proxy).split("http://")[1].split("@")[1]
                options['args'].append(f'--proxy-server={myproxy}')

            else:
                options['args'].append(f'--proxy-server={_proxy}')
        logger.debug('set options %s', options)

        browser = await launch(options)
        page = await browser.newPage()
        await page.setViewport({'width': self.window_width, 'height': self.window_height})
        # 验证用户名和密码
        await page.authenticate({'username': self.username, 'password': self.password})

        if _pretend:
            _default_user_agent = self.default_user_agent
            # get Scrapy request ua, exclude default('Scrapy/2.5.0 (+https://scrapy.org)')
            if 'Scrapy' not in request.headers.get('User-Agent').decode():
                _default_user_agent = request.headers.get('User-Agent').decode()
            await page.setUserAgent(_default_user_agent)
            logger.debug('PRETEND_SCRIPTS is run')
            for script in PRETEND_SCRIPTS:
                await page.evaluateOnNewDocument(script)

        # set cookies
        parse_result = urllib.parse.urlsplit(request.url)
        domain = parse_result.hostname
        _cookies = []
        if isinstance(request.cookies, dict):
            _cookies = [{'name': k, 'value': v, 'domain': domain}
                        for k, v in request.cookies.items()]
        else:
            for _cookie in _cookies:
                if isinstance(_cookie, dict) and 'domain' not in _cookie.keys():
                    _cookie['domain'] = domain
        await page.setCookie(*_cookies)

        # the headers must be set using request interception
        await page.setRequestInterception(self.enable_request_interception)

        if self.enable_request_interception:
            @page.on('request')
            async def _handle_interception(pu_request):
                # handle headers
                overrides = {
                    'headers': pu_request.headers
                }
                # handle resource types
                _ignore_resource_types = self.ignore_resource_types
                if request.meta.get('daoke_pyppeteer', {}).get('ignore_resource_types') is not None:
                    _ignore_resource_types = request.meta.get('daoke_pyppeteer', {}).get('ignore_resource_types')
                if pu_request.resourceType in _ignore_resource_types:
                    await pu_request.abort()
                else:
                    await pu_request.continue_(overrides)

        _timeout = self.download_timeout
        if pyppeteer_meta.get('timeout') is not None:
            _timeout = pyppeteer_meta.get('timeout')

        logger.debug('crawling %s', request.url)

        response = None
        try:
            options = {
                'timeout': 1000 * _timeout
            }
            if pyppeteer_meta.get('wait_until'):
                options['waitUntil'] = pyppeteer_meta.get('wait_until')
            logger.debug('request %s with options %s', request.url, options)
            response = await page.goto(
                request.url,
                options=options
            )
        except (PageError, TimeoutError):
            logger.error('error rendering url %s using daoke_pyppeteer', request.url)
            await page.close()
            await browser.close()
            return self._retry(request, 504, spider)

        # wait for dom loaded
        if pyppeteer_meta.get('wait_for'):
            _wait_for = pyppeteer_meta.get('wait_for')
            try:
                logger.debug('waiting for %s', _wait_for)
                if isinstance(_wait_for, dict):
                    await page.waitFor(**_wait_for)
                else:
                    await page.waitFor(_wait_for)
            except TimeoutError:
                logger.error('error waiting for %s of %s', _wait_for, request.url)
                await page.close()
                await browser.close()
                return self._retry(request, 504, spider)

        # evaluate script
        if pyppeteer_meta.get('script'):
            _script = pyppeteer_meta.get('script')
            logger.debug('evaluating %s', _script)
            await page.evaluate(_script)

        # page.click
        if pyppeteer_meta.get('click'):
            _click = pyppeteer_meta.get('click')
            logger.debug('evaluating %s', _click)
            clickSeeAllWorkspaces = await page.waitForSelector(_click)
            await clickSeeAllWorkspaces.click()

        # sleep
        _sleep = self.sleep
        if pyppeteer_meta.get('sleep') is not None:
            _sleep = pyppeteer_meta.get('sleep')
        if _sleep is not None:
            logger.debug('sleep for %ss', _sleep)
            await asyncio.sleep(_sleep)

        content = await page.content()
        body = str.encode(content)

        # screenshot
        # TODO: maybe add support for `enabled` sub attribute
        _screenshot = self.screenshot
        if pyppeteer_meta.get('screenshot') is not None:
            _screenshot = pyppeteer_meta.get('screenshot')
        screenshot = None
        if _screenshot:
            # pop path to not save img directly in this middleware
            if isinstance(_screenshot, dict) and 'path' in _screenshot.keys():
                _screenshot.pop('path')
            logger.debug('taking screenshot using args %s', _screenshot)
            screenshot = await page.screenshot(_screenshot)
            if isinstance(screenshot, bytes):
                screenshot = BytesIO(screenshot)

        # close page and browser
        logger.debug('close daoke_pyppeteer')
        await page.close()
        await browser.close()

        if not response:
            logger.error('get null response by daoke_pyppeteer of url %s', request.url)

        # Necessary to bypass the compression middleware (?)
        response.headers.pop('content-encoding', None)
        response.headers.pop('Content-Encoding', None)

        response = HtmlResponse(
            page.url,
            status=response.status,
            headers=response.headers,
            body=body,
            encoding='utf-8',
            request=request
        )
        if screenshot:
            response.meta['screenshot'] = screenshot
        return response

    def process_request(self, request, spider):
        """
        process request using daoke_pyppeteer
        :param request:
        :param spider:
        :return:
        """
        logger.debug('processing request %s', request)
        return as_deferred(self._process_request(request, spider))

    async def _spider_closed(self):
        pass

    def spider_closed(self):
        """
        callback when spider closed
        :return:
        """
        return as_deferred(self._spider_closed())
