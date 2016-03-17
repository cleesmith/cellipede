# The MIT License (MIT)
# cellipede Copyright (c) 2015 Chris L. Smith

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
from app import flask_app, datetime, db
import re
from multiprocessing.pool import ThreadPool as Pool
import requests
import bs4
from peewee import *

# ________________________________________________________________________

class Sheet(Model):
  name = CharField()
  run_at = CharField(null=True) # Autorun
  gspread_link = CharField(null=True) # echo/mirror to this google spreadsheet
  atype = CharField(default="plain") # plain or custom
  asheet = TextField(null=True)
  created_at = DateTimeField(null=True)
  updated_at = DateTimeField(null=True)

  class Meta:
    database = db
    db_table = 'sheets'

  def get_id(self):
    try:
      return unicode(self.id) # python 2
    except NameError:
      return str(self.id) # python 3

  def __repr__(self):
    # return '<id {}'.format(self.id)
    return 'id={}, name={}'.format(self.id, self.name)
