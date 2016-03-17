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
from flask.ext.script import Manager
from app import flask_app, datetime, db
from app.sheets.models import Sheet
from apscheduler.schedulers.blocking import BlockingScheduler
from jobs import *
from waitress import serve

flask_app.config.from_object('config.ProductionConfig')

manager = Manager(flask_app)

# usage: python manage.py jobs
@manager.command
def jobs():
  """ Run background job scheduler.
      This is just a simple scheduler with no job persistence(no Redis),
      and run as a separate process from the flask app.
  """
  scheduler = BlockingScheduler()
  # *************
  # schedule jobs:
  # *************
  # see: http://apscheduler.readthedocs.org/en/latest/modules/triggers/cron.html
  # scheduler.add_job(trending, 'cron', day_of_week='*', hour=12) # every day at 12pm
  # scheduler.add_job(trending, 'cron', week='*', day_of_week='sun') # weekly on Sunday
  # scheduler.add_job(trending, 'cron', hour='*/6', args=['daily']) # every 6 hours
  scheduler.add_job(trending, 'cron', hour='18', args=['daily']) # every day at 6pm
  # scheduler.add_job(trending, 'cron', minute='*/1', args=['daily'])
  # scheduler.add_job(trending, 'cron', second='*/5', args=['daily']) # every 5 seconds
  scheduler.add_job(odesk_rss, 'cron', hour='12', args=['daily', 'rails']) # every day at noon
  # *************
  print('Job scheduler started at: %s'%datetime.utcnow())
  scheduler.start()

# usage: python manage.py db_create
@manager.command
def db_create():
  db.connect()
  Sheet.drop_table(True)
  Sheet.create_table(True)
  db.close()

# usage: python manage.py waitress_please
@manager.command
def waitress_please():
  serve(flask_app, port=80) # use waitress

if __name__ == '__main__':
  manager.run()
