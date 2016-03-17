# Cellipede

***

## Advantages
* One of the most important new features is **native spreadsheets** via a jquery plugin called Handsontable.
Handsontable is similar to other spreadsheet software in terms of UI/UX, and it offers the usual excel-like formulas.
* The sheets created are stored in a small sqlite/peewee database for later retrieval.
* Social media metrics and user functions are also provided.
* An intelligent generic scraper is provided, so if **lxml** is installed it will use that,
but if it isn't it will use **beautifulsoup**.
This makes using cellipede on Windows much easier and without compiler issues.
* No google spreadsheets api (gdata) is required, so it's must faster and way more reliable.
Of course, you can copy/paste into google spreadsheets if you need to collaborate/share.
Even better, use cellipede as a service to grab the data you want while in a google spreadsheet.
If you're learning to program, this is a much better example of software to learn from as
it follows well known **best practices** for python and flask apps.
* Includes a job scheduler to run tasks periodically for trending counts and anything over time.
It may also be used for custom jobs, such as the included non-seo example RSS feed parser.
It reads **ruby on rails** job postings from oDesk's RSS feed and fills in a sheet every day.
* There is no login or password, but it's easy to add if you want your cellipede to be multi-user
* You don't have to save a sheet just to try the demo, so go ahead kick the tires and play around, but you can save sheets if you want to
* There is no __exclusive alpha/beta tester program__, just give it a try
* It runs great on a cheap $5 per month server in the cloud like at DigitalOcean
* It runs great on Heroku, for free, well, if you stay below the 10,000 rows maximum for the free database,
but that's a lot of sheets ... and each sheet has no row/column limit.
* It runs great on a Mac, Ubuntu, or Debian ... probably others too
* It runs great on a Raspberry Pi
* There is a lot of potential for learning and growth with cellipede, so let your imagination run wild,
but please let everyone know if you create something cool.

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

> Actually, if you have python and pip installed it's the same steps as a Mac, except for step 3 which should be:
```
3. pip install -r windows_requirements.txt
```
* The above does not include **lxml** which is difficult to install on Windows, so cellipede will use **BeautifulSoup** instead.
* If python 3+ is installed cellipede will not work.  A __todo__ is to make cellipede compatible with both
python 2.7+ and 3+.

***
***
