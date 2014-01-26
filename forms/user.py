# -*- coding: utf-8 -*-

import models

from flaskext.wtf import TextField
from flaskext.wtf import Required
from flaskext.wtf import Regexp
from flaskext.wtf import SubmitField
from flaskext.wtf import PasswordField
from flaskext.wtf import Form
from flaskext.wtf import Email

from flaskext.wtf.html5 import EmailField

from wtforms.validators import ValidationError

import server

class UserForm(Form):

    email = EmailField('E-mail adresse',
                       [Required('Hmm, husk du skal indtaste en E-mail adresse'),
                        Email('Hey, E-mail adressen er ikke gyldig!')],
                        description=u'Så vi kan tjekke at du er fra et godkendt uddannelsessted',
                       )

    username = TextField('Brugernavn',
                         [
            Required(u'Kammerat, du skal vælge et brugernavn!'),
            Regexp(r'^[a-z]+$', message=u'Brugernavnet skal bestå af små bogstaver!')
            ])

    password = PasswordField('Kodeord', [Required('Du mangler at indtaste et kodeord')],)
    password2 = PasswordField('Gentag kodeord', [Required(u'Du mangler at bekræfte kodeord')],)

    submit = SubmitField('Registrer')

    def validate_email(self, field):
        q = models.db.session.query(models.User.email)
        if q.filter_by(email=field.data).first():
            raise ValidationError("E-mail adressen findes allerede. "
                                  "Angiv en anden.")

    def validate_username(self, field):
        q = models.db.session.query(models.User.username)
        if q.filter_by(username=field.data).first():
            raise ValidationError(u"Desværre - det brugernavn er ikke ledigt")
        if server.user_check(field.data):
            raise ValidationError(u"Desværre - det brugernavn er ikke ledigt")

    def validate_password(self, field):
        """Ensure the strength of the password.
        """
        if len(field.data) < 6:
            raise ValidationError(u"Koden skal være mindst 6 karakterer.")
        # For an easy strength checker see:
        # http://passwordadvisor.com/CodePython.aspx

    def validate_password2(self, field):
        """Ensure the strength of the password.
        """
        if self.password.data != field.data:
            raise ValidationError(u"Koder matcher ikke.")
