#!/usr/bin/env python

from json import JSONDecoder
import os
import subprocess
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

    site_affected = False
    encoder_affected = False
    to_explore = ['added', 'removed', 'modified']
    for commit in payload['commits']:
      for category in to_explore:
        for _file in commit[category]:
          _dirname = os.path.dirname(_file)
          if 'site-encoder' == _dirname:
            encoder_affected = True
          if 'site' == _dirname or 'site/' in _dirname:
            site_affected = True

    site_path = '/home/httpd/htdocs/cryptogram/'
    encoder_path = '/home/httpd/htdocs/cryptogram/encoder'
    if site_affected or encoder_affected:
      logging.info('Do repo pull.')
      os.chdir('cryptogram')
      puller = subprocess.Popen('git pull', shell=True)
      puller.wait()
      os.chdir('..')

    if site_affected:
      logging.info('Uploading site files to server.')
      os.chdir('cryptogram')
      os.system('scp -q -i ~/.ssh/id_dsa -o UserKnownHostsFile=/dev/null '\
                '-o StrictHostKeyChecking=no -r site/* fast-beaker:%s'
                % site_path)
      os.chdir('..')
      logging.info('Site files updated.')

    if encoder_affected:
      logging.info('Uploading encoder site files to server.')
      os.chdir('cryptogram')
      os.system('scp -q -i ~/.ssh/id_dsa -o UserKnownHostsFile=/dev/null '\
                '-o StrictHostKeyChecking=no -r site-encoder/* fast-beaker:%s'
                % encoder_path)
      os.chdir('..')
      logging.info('Encoder site files updated.')


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
