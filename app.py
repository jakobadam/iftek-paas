# Avoids circular dependencies to app.
import os

import logging
from logging.handlers import SMTPHandler

from flask import Flask
app = Flask('paas')

site_root = os.path.dirname(os.path.abspath(__file__))

if os.environ.get('SETTINGS'):
    # Another way to enable production state do this:
    # $ export SETTINGS=./conf/settings.cfg
    app.config.from_envvar('SETTINGS')    
else:
    app.config.from_pyfile(os.path.join(site_root, 'conf', 'settings.dev.cfg'))

app.config['SITE_ROOT'] = site_root

if app.config['MODE'] == 'production':
    mail_handler = SMTPHandler(app.config.get('EMAIL_SERVER'),
                               'control-server-error@iftek.dk',
                               app.config['ADMINS'], 'skyen.iftek.dk failed')
    mail_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(mail_handler)
