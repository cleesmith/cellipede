from jobs import odesk_rss, trending

# used by Heroku Scheduler
# task: python jobs_runner.py

trending('daily')

odesk_rss('daily', 'rails')
