from json import JSONDecoder
import os
import sys
import logging
import threading
from tornado.options import define, options
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

logging.basicConfig(level=logging.INFO,
                    filename='cryptogram-infrastructure.log',
                    format='%(asctime)-15s %(levelname)8s %(module)20s '\
                      '%(lineno)4d %(message)s')

define("port", default=39668, help="run on the given port", type=int)


class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r"/", MainHandler),
    ]

    settings = dict(
      template_path=os.path.join(os.path.dirname(__file__), 'templates'),
      static_path=os.path.join(os.path.dirname(__file__), 'static')
      )
    tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
  def post(self):
    arg_payload = self.get_argument('payload')
    payload = JSONDecoder().decode(arg_payload)
    logging.info('Payload: %s.' % payload)


class TornadoServer(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)

  def run(self):
    tornado.ioloop.IOLoop.instance().start()


def main(argv):
  # Start user-facing web server.
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado_server = TornadoServer()
  tornado_server.start()


if __name__ == '__main__':
  try:
    main(sys.argv)
  except Exception, e:
    logging.error(str(e))
