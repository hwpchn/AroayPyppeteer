import logging

# scrapy_pyppeteer logging level
DAOKE_PYPPETEER_LOGGING_LEVEL = logging.WARNING

# scrapy_pyppeteer timeout
DAOKE_PYPPETEER_DOWNLOAD_TIMEOUT = 30

# scrapy_pyppeteer browser window
DAOKE_PYPPETEER_WINDOW_WIDTH = 1400
DAOKE_PYPPETEER_WINDOW_HEIGHT = 700

# scrapy_pyppeteer browser default ua
DAOKE_PYPPETEER_DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'

# scrapy_pyppeteer settings
DAOKE_PYPPETEER_HEADLESS = True
DAOKE_PYPPETEER_EXECUTABLE_PATH = None
DAOKE_PYPPETEER_IGNORE_HTTPS_ERRORS = False
DAOKE_PYPPETEER_SLOW_MO = None
DAOKE_PYPPETEER_IGNORE_DEFAULT_ARGS = False
DAOKE_PYPPETEER_HANDLE_SIGINT = True
DAOKE_PYPPETEER_HANDLE_SIGTERM = True
DAOKE_PYPPETEER_HANDLE_SIGHUP = True
DAOKE_PYPPETEER_DUMPIO = False
DAOKE_PYPPETEER_DEVTOOLS = False
DAOKE_PYPPETEER_AUTO_CLOSE = True
DAOKE_PYPPETEER_PRETEND = True
# scrapy_pyppeteer args
DAOKE_PYPPETEER_DISABLE_EXTENSIONS = True
DAOKE_PYPPETEER_HIDE_SCROLLBARS = True
DAOKE_PYPPETEER_MUTE_AUDIO = True
DAOKE_PYPPETEER_NO_SANDBOX = True
DAOKE_PYPPETEER_DISABLE_SETUID_SANDBOX = True
DAOKE_PYPPETEER_DISABLE_GPU = True

# ignore resource types, ResourceType will be one of the following: ``document``,
# ``stylesheet``, ``image``, ``media``, ``font``, ``script``,
#  ``texttrack``, ``xhr``, ``fetch``, ``eventsource``, ``websocket``,
#  ``manifest``, ``other``.
DAOKE_PYPPETEER_IGNORE_RESOURCE_TYPES = []
DAOKE_PYPPETEER_SCREENSHOT = None
DAOKE_PYPPETEER_SLEEP = 1
DAOKE_ENABLE_REQUEST_INTERCEPTION = True



