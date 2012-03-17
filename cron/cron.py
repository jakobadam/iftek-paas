# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime

import paas
from models import Job
import urllib2
import mail

today = date.today()
now = datetime.now()

jobs = Job.query.filter(Job.last_run < today).filter(Job.hour >= now.hour).all()

for j in jobs:
    try:
        urllib2.urlopen(j.url).read()
    except Exception, e:
        mail.send(receivers=[j.user.email], subject=u'Fejl ved kørsel af job', text=str(e))
