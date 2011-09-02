#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#

import flaskext.wtf
import flaskext.wtf.html5

def _wrap(origclass):
    class WrappingInput(origclass):
        def __init__(self, error_class=u'has_errors'):
            super(WrappingInput, self).__init__()
            self.error_class = error_class

        def __call__(self, field, **kwargs):
            if field.errors:
                cls = kwargs.pop('class', '') or kwargs.pop('class_', '')
                if cls:
                    cls = ' '.join(cls.split(' ') + [self.error_class])
                else:
                    cls = self.error_class
                kwargs['class'] = cls

            if 'required' in field.flags:
                kwargs['required'] = 'required'

            return super(WrappingInput, self).__call__(field, **kwargs)

    WrappingInput.__name__ = origclass.__name__

    return WrappingInput

flaskext.wtf.TextInput = _wrap(flaskext.wtf.TextInput)
flaskext.wtf.PasswordInput = _wrap(flaskext.wtf.PasswordInput)
flaskext.wtf.html5.EmailInput = _wrap(flaskext.wtf.html5.EmailInput)

