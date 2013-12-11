#!/usr/bin/env python
import sys
import paas
from models import User, db

from flask import Flask

if len(sys.argv) < 3:
    sys.exit('useradd.py <user> <pwd> <email>')

app = Flask('paas.py')
with app.app_context():
    user = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3]

    # add linux and mysql user
    User.useradd(user, password)

    # add user to skyen db
    user = User(username=user, password=password, email=email)
    db.session.add(user)
    db.session.commit()

    print 'user added'
