# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#

import models

from flaskext.wtf import TextField
from flaskext.wtf import Required
from flaskext.wtf import SubmitField
from flaskext.wtf import PasswordField
from flaskext.wtf import Form
from flaskext.wtf import Email

from flaskext.wtf.html5 import EmailField

from wtforms.validators import ValidationError

class UserForm(Form):

    email = EmailField('E-mail adresse',
                       [Required('Hmm, husk du skal indtaste en E-mail adresse'),
                        Email('Hey, E-mail adressen er ikke gyldig!')]
                       )

    username = TextField('Brugernavn',
                         [Required(u'Kammerat, du skal vælge et brugernavn!')]
                         )

    password = PasswordField('Kodeord', [Required('Du mangler at indtaste et kodeord')],)

    submit = SubmitField('Registrer')

    def validate_email(self, field):
        q = models.db.session.query(models.User.email)
        if q.filter_by(email=field.data).first():
            raise ValidationError("E-mail adressen findes allerede. "
                                  "Angiv en anden.")

    def validate_password(self, field):
        """Ensure the strength of the password.
        """
        if len(field.data) < 6:
            raise ValidationError(u"Koden skal være mindst 6 karakterer.")
        # For an easy strength checker see:
        # http://passwordadvisor.com/CodePython.aspx

