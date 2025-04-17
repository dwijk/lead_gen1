from django_cron import CronJobBase, Schedule
from datetime import datetime

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 5 # every 2 hours
    schedule = Schedule(run_every=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'    # a unique code
    def do(self):
        print("Hello World")