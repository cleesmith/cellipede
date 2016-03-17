from app import datetime, parse_date
from app.sheets.models import Sheet
from app.sheets.server_sides import ServerSides
from StringIO import StringIO
import feedparser
import json
import re

def all_nones(row):
  if type(row) is not list:
    return True
  return row.count(None) == len(row)

def remove_empty_rows(rows):
  new_sheet = []
  if type(rows) is not list:
    return new_sheet
  for row in rows:
    if all_nones(row):
      continue
    else:
      clean_row = []
      for cell in row:
        clean_row.append(str(cell))
      new_sheet.append(clean_row)
  return new_sheet

def process_row(row, sheet_list):
  # overview:
  # - copy processed row to a new row by:
  #   - keeping empty/None cells
  #   - processing cells beginning with '?'
  #   - otherwise keeping cell 'as is'
  # format='%a %b %d, %Y %T'
  format='%Y/%m/%d %T'
  new_row = []
  if type(row) is not list:
    return new_row
  for c, cell in enumerate(row):
    if c == 0:
      # timestamp this row
      now = str(parse_date(str(datetime.utcnow())).strftime(format))
      new_row.append(str(now))
      continue
    if cell is None:
      new_row.append('null')
      continue
    if (len(cell) > 0) and (cell[0] == '?'):
      # only process cells with '?' as 1st char
      #   - which cell is being referenced ???
      #     e.g. ?tweets(a1) how to grab a1 ?
      #     - use code like chrToNum from sheet.html
      #     - ensure only row 2, really 1, is referenced
      # remove '?', '(', ')', and leading/trailing whitespace:
      func_params = re.sub(r'[\?,),(]', r' ', cell).strip()
      # split by space, so parts [0]=func [1]=cell reference:
      parts = func_params.split(' ')
      afunc = parts[0]
      cell_ref = parts[1] # ignore any other params
      cell_ref_col_letter = cell_ref[0] # can be any col A-Za-z (0-25)
      cell_ref_col_num = ord(cell_ref_col_letter) % 32 - 1
      cell_ref_row = cell_ref[1:] # this must ref row 2 only, but any col
      if cell_ref_row == '2':
        param = sheet_list[int(cell_ref_row)-1][int(cell_ref_col_num)]
        try:
          func_result = getattr(ServerSides, afunc)(param)
          result = func_result
        except Exception as e:
          result = "Error: running function: %s ... exception: %s" % (cell, e)
        new_row.append(str(result))
      else:
        new_row.append(str("INVALID row: must be 2, but was (%s) in %s" % (cell_ref, cell)))
    else:
      # new_row.append(str(cell)) # use 'null' instead any existing cell value:
      new_row.append('null')
  return new_row

def trending(run_at):
  # a sheet template for trending must be like this:
  # row 1 is the headers
  # row 2:
  #   col 1+ are the function params (url/user) - may be multiples
  #   trailing col's are the ?func(x2)'s to be performed
  # after each run row 3+ will be the results:
  # row 3:
  #   col 1 is the timestamp
  #   col 2+ are the result of each ?func call
  # note: without some fixed layout this would difficult to perform, also
  #       since it's basically a report it would be ugly/unreadable if
  #       there wasn't a layout
  # print("%s run_at=%s"%(datetime.utcnow(),run_at))
  # return
  sheets = Sheet.select()
  for sheet in sheets:
    if sheet.name.lower()[0:9] == 'odesk rss':
      continue
    if sheet.run_at == 'never':
      continue
    elif sheet.run_at == run_at:
      processed_sheet = []
      buf = StringIO(sheet.asheet)
      sheet_dict = json.load(buf)
      sheet_list = sheet_dict['data']
      sheet_list = remove_empty_rows(sheet_list)
      for x, row in enumerate(sheet_list):
        # ignore the first row, x == 0
        # process the second row, x == 1
        # ignore all other rows/cols
        if (x == 0) or all_nones(row):
          continue
        elif x == 1: # only process row 2
          processed_sheet.append(process_row(row, sheet_list))
        else:
          continue
      for ps in processed_sheet:
        sheet_list.append(ps)
      # store in db with the same format as handsontable i.e. JSON.stringify(hot.getData()):
      new_sheet_str = "{'data': " + str(sheet_list).replace('None', '').replace('null', '') + "}"
      new_sheet_str = new_sheet_str.replace("'", '"')
      sheet.asheet = new_sheet_str
      sheet.updated_at = datetime.utcnow()
      sheet.save()
    print("%s Completed autorun trending job: processed sheet '%s'" % (datetime.utcnow(), sheet.name))

def clear_sheet(sheet):
  clean_row = []
  for cell in sheet[0]:
    if cell is None or cell == '':
      cell = 'null'
    clean_row.append(str(cell)) # use str() to remove unicode (u'...')
  return [clean_row]

def odesk_rss(run_at, query):
  format='%Y/%m/%d %T'
  sheets = Sheet.select()
  for sheet in sheets:
    if sheet.name.lower()[0:9] != 'odesk rss':
      continue
    if sheet.run_at == 'never':
      continue
    elif sheet.run_at == run_at:
      processed_sheet = []
      buf = StringIO(sheet.asheet)
      sheet_dict = json.load(buf)
      sheet_list = sheet_dict['data']
      sheet_list = clear_sheet(sheet_list)
      try:
        feeder = feedparser.parse('https://www.odesk.com/jobs/rss?q=' + query)
        for posted_job in feeder.entries:
          new_row = []
          # pubdate = str(parse_date(str(posted_job.published)).strftime(format))
          # new_row.append(str(pubdate))
          # new_row.append(str(posted_job.title))
          # new_row.append(str(posted_job.link))
          pubdate = parse_date(str(posted_job.published)).strftime(format)
          new_row.append(pubdate)
          new_row.append(posted_job.title.encode('ascii', 'ignore'))
          new_row.append(posted_job.link.encode('ascii', 'ignore'))
          # now = str(parse_date(str(datetime.utcnow())).strftime(format))
          # new_row.append(str(now))
          processed_sheet.append(new_row)
      except Exception as e:
        # ERROR: Error: running function: odesk_rss ... exception: 'ascii' codec can't encode character u'\u0421' in position 0: ordinal not in range(128)
        # a solution: ".encode('ascii', 'ignore')" as "str()" doesn't work
        error = "Error: running function: odesk_rss ... exception: %s" % e
        new_row.append(str(error))
        processed_sheet.append(new_row)
      for ps in processed_sheet:
        sheet_list.append(ps)
      # store in db with the same format as handsontable i.e. JSON.stringify(hot.getData()):
      new_sheet_str = "{'data': " + str(sheet_list).replace('None', "").replace('null', "") + "}"
      new_sheet_str = new_sheet_str.replace("'", '"')
      sheet.asheet = new_sheet_str
      sheet.updated_at = datetime.utcnow()
      print("updated=%s name=%s"%(sheet.updated_at,sheet.name))
      ssresp = sheet.save()
      print("sheet.save() response:")
      print(ssresp)
    print("%s Completed '%s' autorun of oDesk RSS job: query: '%s' processed sheet '%s'" % (datetime.utcnow(), run_at, query, sheet.name))
