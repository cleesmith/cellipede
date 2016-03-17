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

import os, json
from app import flask_app, time, datetime, parse_date, db
from flask import flash, jsonify, redirect, session, Response, url_for, render_template, Blueprint, request, send_from_directory
from flask.ext.login import login_required
from flask.ext.login import current_user
# from jinja2 import Environment
import jinja2
from app.sheets.models import Sheet
from app.sheets.forms import SheetForm
import requests
from playhouse.csv_loader import *
from server_sides import ServerSides
from StringIO import StringIO

sheets_blueprint = Blueprint('sheets', __name__, template_folder='templates')

errors = []

def basename(value):
  return os.path.basename(value)
jinja2.filters.FILTERS['basename'] = basename

def format_number(value):
  return "{:,}".format(value)
jinja2.filters.FILTERS['format_number'] = format_number

def datetimeformat(value, format='%a %B %d, %Y %T'):
  if value is None or '':
    return ''
  return parse_date(str(value)).strftime(format)
jinja2.filters.FILTERS['datetimeformat'] = datetimeformat

@sheets_blueprint.route('/')
def overview():
  return render_template('overview.html')

@sheets_blueprint.route('/sheets')
def sheets_list():
  sheets = Sheet.select()
  return render_template('sheets_list.html', current_user=current_user, sheets=sheets)

@sheets_blueprint.route('/sheet')
def sheet():
  id = request.args.get('id', None)
  if id is None:
    sheet = Sheet(id='null', name='', run_at='never', asheet='{"data": null}')
  else:
    sheet = Sheet.get(Sheet.id==id)
    if sheet.asheet is None:
      sheet.asheet = '{"data": null}'
  sheet_form = SheetForm(None, sheet)
  return render_template('sheet.html', current_user=current_user,
    form=sheet_form,
    sheet_id=sheet.id,
    sheet_name=sheet.name,
    sheet_run_at=sheet.run_at,
    sheet_updated_at=sheet.updated_at,
    asheet=sheet.asheet
  )

@sheets_blueprint.route('/sheet_as_table')
def sheet_as_table():
  # in a cell in a google spreadsheet do:
  #   =IMPORTHTML("http://cellipede.com/sheet_as_table?id=2","table",1)
  #   which will import the 1st html table found at this url: i.e. the "table",1
  sheet_list = []
  id = request.args.get('id', None)
  if id is None:
    return 'Error: sheet id is missing!'
  else:
    try:
      sheet = Sheet.get(Sheet.id==id)
      buf = StringIO(sheet.asheet)
      sheet_dict = json.load(buf)
      sheet_list = sheet_dict['data']
    except Exception as e:
      return 'Error: sheet id or data is invalid!'
  return render_template('sheet_as_table.html', current_user=current_user, asheet=sheet_list )

@sheets_blueprint.route('/sheet_delete')
def sheet_delete():
  flash('Sheet deletion is disabled for this demo!')
  return redirect(url_for('sheets.sheets_list'))
  id = request.args.get('id', None)
  if id is None:
    flash('Error: sheet id is missing!')
  else:
    q = Sheet.delete().where(Sheet.id==id)
    res = q.execute()
    flash('Sheet was deleted')
  return redirect(url_for('sheets.sheets_list'))

@sheets_blueprint.route('/sheet_save', methods=['POST'])
def sheet_save():
  id = request.form.get('id', None)
  # coz blank is something and not None:
  id = None if id == '' else id
  if id is None:
    sheet = Sheet(name='')
  else:
    sheet = Sheet.get(Sheet.id==id)
  name = request.form.get('name', None)
  # coz blank is something and not None:
  name = None if name == '' else name
  if name is None:
    return jsonify({'result': 'Error: a sheet name is required!'})
  run_at = request.form.get('run_at', 'never')
  # # coz blank is something and not None:
  # run_at = None if run_at == '' else run_at
  # if run_at is None:
  #   run_at = 'never'
  sheet.name = name
  sheet.run_at = run_at
  sheet.asheet = """{"data": """ + request.form.get('asheet', None) + "}"
  sheet.updated_at = datetime.datetime.utcnow()
  sheet.save()
  return jsonify({'result': 'ok'})

@sheets_blueprint.route('/sheet_serverside', methods=['POST'])
def sheet_serverside():
  resp = 'ok'
  id = request.form.get('id', None)
  func = request.form.get('afunction', None)
  url = request.form.get('url', None)
  result = ''
  try:
    func_result = getattr(ServerSides, func)(url)
    result = func_result
  except Exception as e:
    resp = "Error: running function: %s ... exception: %s" % (func, e)
    result = None
  return jsonify({'result': resp, 'raw_data': result})

@sheets_blueprint.route('/sheet_function')
def sheet_function():
  # =IMPORTHTML("http://cellipede.com/sheet_function?afunction=tweets&url=http://www.amazon.com/","table",1)
  func = request.args.get('afunction', None)
  url = request.args.get('url', None)
  result = ''
  try:
    func_result = getattr(ServerSides, func)(url)
    result = func_result
  except Exception as e:
    resp = "Error: running function: %s ... exception: %s" % (func, e)
    result = None
  return render_template('sheet_function_as_table.html', func=func, url=url, result=result )
