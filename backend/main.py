import os
import sys

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

import tornado.web
import tornado.httpserver
import tornado.ioloop
from backend.tools.get_host_ip import host_ip
from backend.webInterface import ocrtext,findtext
from backend.tools import log
import logging
logger = logging.getLogger(log.LOGGER_ROOT_NAME+'.'+__name__)

current_path = os.path.dirname(__file__)


def make_app():
    return tornado.web.Application([
        (r"/api/ocrtext/", ocrtext.OcrText),
        (r"/api/findtext/", findtext.FindText),
    ])


if __name__ == "__main__":

    port = 8099
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    # server.listen(port)
    server.bind(port)
    server.start(1)
    print(f'server is running: {host_ip()}:{port}')

    # tornado.ioloop.IOLoop.instance().start()
    tornado.ioloop.IOLoop.current().start()
