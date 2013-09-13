# -*- coding: utf-8 -*-

"""WebHelpers used in ebetl."""
import sys
from webhelpers import date, feedgenerator, html, number, misc, text
from datetime import datetime

import sys
import os
import re
import codecs
import io
import collections


# pychecker gets confused by __next__ for Python 3 support.
__pychecker__ = 'no-special'



if sys.version >= '3':
    _string_types = str
    _text_type = str
else:
    _string_types = basestring
    _text_type = unicode

def current_year():
  now = datetime.now()
  return now.strftime('%Y')

def icon(icon_name, white=False):
    if (white):
        return html.literal('<i class="icon-%s icon-white"></i>' % icon_name)
    else:
        return html.literal('<i class="icon-%s"></i>' % icon_name)
        

class AtomicFile(object):
    """Facilitate atomic writing of files.  Forces UTF-8 encoding."""

    def __init__(self, filename):
        self.filename = filename
        if sys.version_info[0] < 3:
            self.fd = codecs.open(
                '%s.new' % self.filename, 'w', 'latin-1', 'replace')
        else:
            # io.open is available from Python 2.6, but we only use it with
            # Python 3 because it raises exceptions when passed bytes.
            self.fd = io.open(
                '%s.new' % self.filename, mode='w',
                encoding='UTF-8', errors='replace')

    def __enter__(self):
        return self.fd

    def __exit__(self, exc_type, unused_exc_value, unused_exc_tb):
        self.fd.close()
        if exc_type is None:
            os.rename('%s.new' % self.filename, self.filename)

    # Not really necessary, but reduces pychecker confusion.
    def write(self, s):
        self.fd.write(s)
