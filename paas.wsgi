import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS = SITE_ROOT + '/conf/settings.cfg'

sys.path.append(SITE_ROOT)
os.environ['SETTINGS'] = os.path.join(SITE_ROOT, SETTINGS)

activate_this = SITE_ROOT + '/../env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from control import app as application
