#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#

import models

from flaskext.wtf import Form
from flaskext.wtf import SubmitField
from flaskext.wtf.html5 import EmailField
from flaskext.wtf import PasswordField
from flaskext.wtf import ValidationError
from flaskext.wtf import Email
from flaskext.wtf import Required

class LoginForm(Form):

    email = EmailField('E-mail adresse',
                       [Required('Hmm, husk du skal indtaste en E-mail adresse'),
                        Email('Hey, E-mail adressen er ikke gyldig!')]
                       )

    password = PasswordField('Kodeord',
                         [Required('Indtast et kodeord')],
                         description='<a href="/reset-password">Har du glemt koden?</a>')

    login = SubmitField('Luk mig ind')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate_email(self, field):
        if not self.email.data or not self.password.data:
            return

        user = models.User.query.filter_by(email=self.email.data).first()
        if not user or not user.check_password(self.password.data):
            raise ValidationError('Unrecognized email or password.')
        
        self.user = user
        status = self.user.status
 
        if status == models.User.STATUS_LOCKED:
            raise ValidationError('This account is locked.')
        elif status == models.User.STATUS_NEW:
            raise ValidationError('This account email has not been verified.')
        
