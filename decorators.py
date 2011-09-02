from functools import wraps

from flask import g
from flask import redirect
from flask import request
from flask import url_for
from flask import flash

############
# decorators
############

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is not None:
            return f(*args, **kwargs)
        return redirect('/?continue=' + request.url, 302)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is not None and g.user.is_staff:
            return f(*args, **kwargs)
        return "Yo, this is a admin only area!", 400
    return decorated_function
    
