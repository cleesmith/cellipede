from itertools import *
import collections
import requests
import xml.dom.minidom
from xml.dom.minidom import parseString
import bs4
from bs4 import BeautifulSoup
import re
try:
  import lxml.html
  LXML_FOUND = True # soup/sandwich :)
except:
  LXML_FOUND = False # only soup for you

def slice_string(input_string):
  input_string = input_string.lstrip("/url?q=")
  index_c = input_string.find('&')
  input_string = input_string[:index_c]
  return input_string

def scrape_with_lxml(url, search_for, search_type, search_pattern):
  result = ''
  try:
    resp = requests.get(url)
    html = resp.text
    if search_type == 'xpath':
      page_tree = lxml.html.fromstring(html)
      match = page_tree.xpath(search_pattern)
      if match:
        result = match[0]
      else:
        result = 'not found'
    elif search_type == 'regex':
      match = re.search(search_pattern, html, re.S | re.I)
      if match:
        if "scrape" in match.groupdict().keys():
          result = match.group("scrape")
        else:
          result = 'not found'
      else:
        result = 'not found'
  except Exception as e:
    result = "Error: can not scrape url: %s\nexception: %s" % (url, e)
  return result

def get_html_with_bs4(url):
  error = None
  soup = None
  try:
    # page = requests.get(
    #   video_data['url'],
    #   headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'}
    # )
    # fool'em: no spider just firefox:
    firefox_header = {'User-agent': 'Mozilla/5.0'}
    page = requests.get(url, headers=firefox_header)
    page.raise_for_status() # if not 200 raise an exception
    raw_html = page.text
    # remove comments, to avoid BeautifulSoup hiccups:
    clean_html = re.sub(r'<!--.*?-->', r'', raw_html.encode('utf-8'), flags=re.DOTALL)
    soup = BeautifulSoup(clean_html)
  except Exception as e:
    error = "Error: can not scrape url: %s\nexception: %s" % (url, e)
  return (page.text, soup, error)

class ServerSides(object):
  # use the @staticmethod decorator, so these funcs can be seen by "dir" and "getattr"

  # any ole web page stuff
  @staticmethod
  def title(url):
    if LXML_FOUND:
      response = scrape_with_lxml(url, 'title', 'xpath', "//title/text()")
    else:
      page, soup, error = get_html_with_bs4(url)
      if error:
        return error
      try:
        response = soup.title.text
      except:
        response = ''
    return response

  @staticmethod
  def description(url):
    if LXML_FOUND:
      response = scrape_with_lxml(url, 'description', 'xpath', '//meta[@name="description"]/@content')
    else:
      page, soup, error = get_html_with_bs4(url)
      if error:
        return error
      try:
        descr = soup.findAll('meta', attrs={'name':'description'})
        if len(descr) > 0:
          response = descr[0].get('content')
        else:
          response = ''
      except:
        response = ''
    return response

  @staticmethod
  def ga(url):
    response = ''
    search_pattern = "(?:\'|\")(?P<scrape>UA-.*?)(?:\'|\")"
    if LXML_FOUND:
      response = scrape_with_lxml(url, 'ga', 'regex', search_pattern)
    else:
      page, soup, error = get_html_with_bs4(url)
      if error:
        return error
      try:
        match = re.search(search_pattern, page, re.S | re.I)
        if match:
          if "scrape" in match.groupdict().keys():
            response = match.group("scrape")
      except Exception as e:
        response = ''
    return response

  # YouTube stuff
  @staticmethod
  def subscribers(user):
    try:
      response = requests.get('http://gdata.youtube.com/feeds/api/users/' + user)
      dom = parseString(response.text)
      stats = dom.getElementsByTagNameNS("http://gdata.youtube.com/schemas/2007","statistics")
      count = stats[0].getAttribute("subscriberCount")
      count = "{:,}".format(int(count))
    except Exception as e:
      count = "Error: no subscribers count returned from youtube api: %s\nexception: %s" % (user, e)
    return count

  @staticmethod
  def totalviews(user):
    try:
      response = requests.get('http://gdata.youtube.com/feeds/api/users/' + user)
      dom = parseString(response.text)
      stats = dom.getElementsByTagNameNS("http://gdata.youtube.com/schemas/2007","statistics")
      count = stats[0].getAttribute("totalUploadViews")
      count = "{:,}".format(int(count))
    except Exception as e:
      count = "Error: no total views count returned from youtube api: %s\nexception: %s" % (user, e)
    return count

  @staticmethod
  def views(video_id):
    url = 'https://www.youtube.com/watch?v=' + video_id
    page, soup, error = get_html_with_bs4(url)
    if error:
      return error
    try:
      count = int(re.sub('[^0-9]', '', soup.select('.watch-view-count')[0].get_text().split()[0]))
      count = "{:,}".format(count)
    except Exception as e:
      count = "Error: views count not found: %s\nexception: %s" % (url, e)
    return count

  @staticmethod
  def thumbsup(video_id):
    url = 'https://www.youtube.com/watch?v=' + video_id
    page, soup, error = get_html_with_bs4(url)
    if error:
      return error
    try:
      count = int(re.sub('[^0-9]', '', soup.select('#watch-like-dislike-buttons span.yt-uix-button-content')[0].get_text().split()[0]))
      count = "{:,}".format(count)
    except Exception as e:
      count = "Error: thumbsup count not found: %s\nexception: %s" % (url, e)
    return count

  @staticmethod
  def thumbsdown(video_id):
    url = 'https://www.youtube.com/watch?v=' + video_id
    page, soup, error = get_html_with_bs4(url)
    if error:
      return error
    try:
      count = int(re.sub('[^0-9]', '', soup.select('#watch-like-dislike-buttons span.yt-uix-button-content')[2].get_text().split()[0]))
      count = "{:,}".format(count)
    except Exception as e:
      count = "Error: thumbsdown count not found: %s\nexception: %s" % (url, e)
    return count

  @staticmethod
  def videotitle(video_id):
    url = 'https://www.youtube.com/watch?v=' + video_id
    page, soup, error = get_html_with_bs4(url)
    if error:
      return error
    try:
      response = soup.select('span.watch-title')[0].get_text().strip()
    except Exception as e:
      response = "Error: video title not found: %s\nexception: %s" % (url, e)
    return response

  # Twitter user account stuff
  @staticmethod
  def tweettotal(user):
    url = 'https://twitter.com/' + user
    page, soup, error = get_html_with_bs4(url)
    if error:
      return error
    try:
      count_str = soup.select('.ProfileNav-stat--link span.ProfileNav-value')[0].get_text().split()[0]
      if count_str.isdigit():
        count = int(re.sub('[^0-9]', '', soup.select('.ProfileNav-stat--link span.ProfileNav-value')[0].get_text().split()[0]))
        count = "{:,}".format(count)
      else:
        count = count_str
    except Exception as e:
      count = "Error: twitter tweets count not found: %s\nexception: %s" % (user, e)
    return count

  @staticmethod
  def following(user):
    url = 'https://twitter.com/' + user
    page, soup, error = get_html_with_bs4(url)
    if error:
      return error
    try:
      count_str = soup.select('.ProfileNav-stat--link span.ProfileNav-value')[1].get_text().split()[0]
      if count_str.isdigit():
        count = int(re.sub('[^0-9]', '', soup.select('.ProfileNav-stat--link span.ProfileNav-value')[1].get_text().split()[0]))
        count = "{:,}".format(count)
      else:
        count = count_str
    except Exception as e:
      count = "Error: twitter following count not found: %s\nexception: %s" % (user, e)
    return count

  @staticmethod
  def followers(user):
    url = 'https://twitter.com/' + user
    page, soup, error = get_html_with_bs4(url)
    if error:
      return error
    try:
      count_str = soup.select('.ProfileNav-stat--link span.ProfileNav-value')[2].get_text().split()[0]
      if count_str.isdigit():
        count = int(re.sub('[^0-9]', '', soup.select('.ProfileNav-stat--link span.ProfileNav-value')[2].get_text().split()[0]))
        count = "{:,}".format(count)
      else:
        # twitter humanizes large numbers, e.g. 3.75M followers for jenna_marbles or 20.6K tweets for pewdiepie
        count = count_str
    except Exception as e:
      count = "Error: twitter followers count not found: %s\nexception: %s" % (user, e)
    return count

  # Tweets for any url
  @staticmethod
  def tweets(url):
    api = "http://urls.api.twitter.com/1/urls/count.json?url="
    try:
      resp = requests.get(api + url)
      resp.raise_for_status() # do this coz responses other than 200 are not considered exceptions
      adict = resp.json()
      count = adict["count"]
      count = "{:,}".format(int(count))
    except Exception as e:
      count = "Error: no tweets count returned from twitter api: %s\nexception: %s" % (url, e)
    return count

  # Google+ stuff
  @staticmethod
  def plusses(url):
    api = "https://clients6.google.com/rpc"
    jobj = '''{
      "method":"pos.plusones.get",
      "id":"p",
      "params":{
          "nolog":true,
          "id":"%s",
          "source":"widget",
          "userId":"@viewer",
          "groupId":"@self"
          },
      "jsonrpc":"2.0",
      "key":"p",
      "apiVersion":"v1"
    }''' % (url)
    try:
      respobj = requests.post(api, jobj)
      respobj.raise_for_status() # do this coz responses other than 200 are not considered exceptions
      adict = respobj.json()
      count = int(adict['result']['metadata']['globalCounts']['count'])
      count = "{:,}".format(int(count))
    except Exception as e:
      count = "Error: no plusses count returned from google api: %s\nexception: %s" % (url, e)
    return count

  # Facebook stuff
  @staticmethod
  def shares(url):
    api = "https://graph.facebook.com/fql?q=SELECT%20share_count%20FROM%20link_stat%20WHERE%20url%20=%20%27"
    try:
      respobj = requests.get(api + url + "%27")
      respobj.raise_for_status() # do this coz responses other than 200 are not considered exceptions
      adict = respobj.json()
      count = adict['data'][0]['share_count']
      count = "{:,}".format(int(count))
    except Exception as e:
      count = "Error: no shares count returned from facebook api: %s\nexception: %s" % (url, e)
    return count

  @staticmethod
  def likes(url):
    api = "https://graph.facebook.com/fql?q=SELECT%20like_count%20FROM%20link_stat%20WHERE%20url%20=%20%27"
    try:
      respobj = requests.get(api + url + "%27")
      respobj.raise_for_status() # do this coz responses other than 200 are not considered exceptions
      adict = respobj.json()
      count = adict['data'][0]['like_count']
      count = "{:,}".format(int(count))
    except Exception as e:
      count = "Error: no likes count returned from facebook api: %s\nexception: %s" % (url, e)
    return count

  @staticmethod
  def links(url):
    firefox_header = {'User-agent': 'Mozilla/5.0'}
    source_code = requests.get(url, headers=firefox_header)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)
    links = ''
    for link in soup.findAll("a", {"class" : ""}):
      href = link.get('href')
      if href[:4] == 'http':
        links += href + "\n"
    return links

  @staticmethod
  def serps(query):
    # goal: preserve the links listed by google search in the order presented,
    #       as this represents the search rank/position for the given "query"
    links_sorted_by_pos = collections.OrderedDict()
    links = collections.OrderedDict()
    query = query.replace(' ','+')
    url = 'https://www.google.com/search?num=100&q=' + query + '#q=' + query + '&start=0'
    firefox_header = {'User-agent': 'Mozilla/5.0'}
    source_code = requests.get(url, headers=firefox_header)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)
    pos = 1
    for link in soup.findAll("a", {"class" : ""}):
      href = link.get('href')
      link_string = slice_string(href)
      if link_string in links:
        continue
      if link_string == 'http://www.google.com/aclk?sa=l':
        # not sure why this link occurs but let's ignore it ?
        continue
      if link_string[:4] == 'http':
        # using an ordered dict so we get a list of unique links plus their position:
        links[link_string] = pos
        pos += 1
    links_sorted_by_pos = collections.OrderedDict(sorted(links.items(), key=lambda t: t[1]))
    links_string = ''
    for k,v in links_sorted_by_pos.items():
      links_string += "%s. %s\n" % (v, k)
    return links_string
