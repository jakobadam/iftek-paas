import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# create the settings in order not to expose 
# sensitive info.
SETTINGS = SITE_ROOT + '/../settings.cfg'

sys.path.append(SITE_ROOT)
os.environ['SETTINGS'] = os.path.join(SITE_ROOT, SETTINGS)

activate_this = SITE_ROOT + '/../env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from paas import app as application
