# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#

import models

from flaskext.wtf import Form
from flaskext.wtf import Required
from flaskext.wtf import SubmitField
from flaskext.wtf import PasswordField

from flaskext.wtf.html5 import EmailField

from wtforms.validators import ValidationError

from .user import check_password_strength

class RequestResetForm(Form):

    email = EmailField('Email',
                       [Required('Indtast din email-adresse')],
                       description='Din email-adresse')

    signup = SubmitField(u'Fortsæt…')

    def validate_email(self, field):
        q = models.db.session.query(models.User.email)
        if not q.filter_by(email=field.data).first():
            raise ValidationError("Denne email er ikke i brug.")

class VerifiedResetForm(Form):

    password = PasswordField('Nyt kodeord',
                         [Required('Indtast en ny kode')],
                         description='Indtast et nyt kodeord'
        )

    signup = SubmitField('Gem')

    def validate_password(self, field):
        """Ensure the strength of the password.
        """
        check_password_strength(field.data)

        if len(field.data) < 6:
            raise ValidationError(u"Koden skal være mindst 6 karakterer.")
