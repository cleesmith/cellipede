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

from __future__ import print_function
import os
import time
from datetime import datetime
from dateutil.parser import parse as parse_date
from flask import Flask
from flask.ext.login import LoginManager
from flask import flash, redirect, session, url_for, render_template
from flask import request, send_from_directory, g
import jinja2
from functools import wraps
from peewee import *

flask_app = Flask(__name__)

flask_app.config.from_object('config.ProductionConfig') # see config.py

db = SqliteDatabase(flask_app.config['DATABASE'])

@flask_app.before_request
def before_request():
  g.db = db
  g.db.connect()

@flask_app.after_request
def after_request(response):
  g.db.close()
  return response

from app.sheets.views import sheets_blueprint
flask_app.register_blueprint(sheets_blueprint)

# the following is needed coz the app uses "bootstrap" glyphicons:
@flask_app.route('/fonts/<path:filename>')
def send_font(filename):
  static_images = flask_app.static_folder + "/fonts"
  return send_from_directory(static_images, filename)

# the following is needed coz "jquery.dataTables.min.css" refers to images like: "/images/sort_asc.png":
@flask_app.route('/images/<path:filename>')
def send_image(filename):
  static_images = flask_app.static_folder + "/images"
  return send_from_directory(static_images, filename)
