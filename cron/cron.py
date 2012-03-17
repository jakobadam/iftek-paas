# -*- coding: utf-8 -*-
import sys
import os
import urllib2

from datetime import date
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import paas
from models import Job
from models import db
import mail

today = date.today()
now = datetime.now()

jobs = Job.query\
    .filter(Job.hour <= now.hour)\
    .filter((Job.last_run < today ) | (Job.last_run == None))\
    .all()

for j in jobs:
    try:
        urllib2.urlopen(j.url).read()
        j.last_run = now
        db.session.add(j)
    except Exception, e:
        mail.send(receivers=[j.user.email], subject=u'Fejl ved kørsel af job', text=str(e))

db.session.commit()
