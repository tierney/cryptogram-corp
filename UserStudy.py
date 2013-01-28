#!/usr/bin/env python

import time
import re
import sys
import urllib

# ip addr: (\b(?:\d{1,3}\.){3}\d{1,3}\b)
httpRe = re.compile("(.*) - - \[(.*)\] \"(?:GET|POST|HEAD) [^ ]+sev=(.*)&msg=(.*) HTTP/.*")

def from_log_time(str_time):
  return time.mktime(time.strptime(str_time, '%d/%b/%Y:%H:%M:%S -0500'))

def main(argv):
  with open('cryptogram.log.1') as fh:
    while True:
      line = fh.readline()
      if not line:
        break

      m = re.match(httpRe, line)
      if m:
        ip_addr, ts, level, msg =  m.groups()
        print from_log_time(ts), ip_addr, urllib.unquote(msg).strip()

if __name__ == '__main__':
  main(sys.argv)
