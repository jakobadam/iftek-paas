#!/usr/bin/env python
import sys
import paas
import models

from flask import Flask

if len(sys.argv) < 3:
    sys.exit('useradd.py <user> <pwd>')

app = Flask('paas.py')
with app.app_context():
    user = sys.argv[1]
    password = sys.argv[2]
    models.User.useradd(user, password)
    print user
