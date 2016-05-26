# Cellipede

### A python/flask web app for SEO chores.

* Includes **native spreadsheets** via a jquery plugin called Handsontable.
  * Handsontable is similar to other spreadsheet software in terms of UI/UX, and it offers the usual excel-like formulas.
* The sheets created are stored in a small SQLite/peewee database for later retrieval.
* Social media metrics and other functions are provided:
  * see ```app/sheets/server_sides.py``` for details:
    * URL based functions:
      * title - grabs head title tag
      * description - grabs head meta description tag
      * ga - grabs Google's analytics (UA) value
      * links - grabs all ```<a href=``` tags
    * SERP
      * serps - the search rank/position for the given "query" via a Google search
    * YouTube:
      * subscribers
      * totalviews
      * views
      * videotitle
      * thumbsup
      * thumbsdown
    * Twitter
      * tweettotal
      * following
      * followers
      * tweets (any URL) - deprecated by Twitter in 2015
    * Google
      * plusses
    * Facebook
      * shares
      * likes
  * you may add new functions to ```server_sides.py```
* A generic scraper is provided that uses:
  * **lxml** if it's installed
  * **beautifulsoup** if **lxml** is NOT installed
  * this allows it to run on Windows much easier and without dependency build issues
* It does not rely on Google's Spreadsheets API, so it's must faster and way more reliable.
  * Of course, you can copy/paste into google spreadsheets if you need to collaborate/share.
  * Even better, use cellipede as a service to grab the data you want while in a google spreadsheet.
* It includes a job scheduler to run tasks periodically for trending counts and anything over time.
  * It may also be used for custom jobs, such as the included non-seo example RSS feed parser:
    * It reads **ruby on rails** job postings from oDesk/UpWork's RSS feed and fills in a sheet every day.
* There is no login or password, but it's easy to add if you want your cellipede to
be multi-tenant/user as the **code** to do so is provided.
* It runs great on a cheap $5 per month server in the cloud like at DigitalOcean.
* It runs great on Heroku, for free, well, if you stay below the 10,000 rows maximum for the
free database, but that's a lot of sheets and each sheet has no row/column limit.
* It runs great on a Mac, Ubuntu, or Debian, and probably others too.
* It runs great on a Raspberry Pi.
* If you are learning to program, this is a great example of software to learn from as
it follows well known **best practices** for Python and Flask apps.
* This app is great place to start learning about:
  * **python** - a good beginner's programming language
  * **flask** - how web apps work
  * **peewee** - how SQL databases work
  * **OS** - run it on various operating systems (OS) to explore and learn
  * **SEO** - some simple web page scraping and API calling functions are provided

***

## Getting started

***

### Mac OS X

#### install this app and run it in 4 simple steps:
```
1. git clone https://github.com/cleesmith/cellipede.git
   or click on the Download ZIP button then unzip
2. cd cellipede
3. pip install -r requirements.txt
4. python manage.py runserver
```

> now point your browser to http://localhost:5000/

##### or to run all the time on port 80 replace step 4. with:
```
4. nohup python manage.py waitress_please &
```
> then point your browser to http://localhost_or_someIP_or_someDomain/

##### there's a 5th step if you want to run the job scheduler (for trending and rss feeds):
```
5. nohup python manage.py jobs &
```

##### Upstart scripts
> Included are two Upstart scripts to run both the app and the scheduler on server boot and with respawn if they should die.
> See the **etc/init** folder for the two **conf** files, which should be copied to the /etc/init/ folder
on your server.  That's if you wish to run cellipede as a service, which may be controlled with
```sudo service cellipede start/stop/restart```

***

### Linux
> Actually, if you have git, python, and pip installed it's the same steps as a Mac.

***

### Windows
> Download [Tiny Core with Python plus](https://github.com/cleesmith/tinycore_with_python_plus "Tiny Core with Python plus")

**or**

> Actually, if you have python and pip installed then it's the same steps as a Mac, except for step 3 which should be:
```
3. pip install -r windows_requirements.txt
```
* The above does not include **lxml** which is difficult to install on Windows, so cellipede will use **BeautifulSoup** instead.
* If python 3+ is installed cellipede will not work, but a __todo__ is to be compatible with both python 2.7+ and 3+.

***
***
