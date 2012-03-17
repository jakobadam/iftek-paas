# -*- coding: utf-8 -*-

#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#

import models

from flaskext import wtf


class JobForm(wtf.Form):

    url = wtf.html5.URLField('URL', [
        wtf.Required('Hmm, husk du skal at indtaste en URL'),
        wtf.URL('Hey, URLen er ikke gyldig!')
    ])

    hour = wtf.IntegerField(u'Kald URL denne time', [
        wtf.Required(u'Indtast timen hvor jobbet skal køres'),
        wtf.NumberRange(min=0, max=23, message='Indtast et tal fra 0 til 23')
    ])

    submit = wtf.SubmitField('Opret')
