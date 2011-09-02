from app import app

from flask import g
from flask import url_for

def inject_user():
    """Injects the user into templates"""
    if g.user:
        return dict(user=g.user, logout_url=url_for('logout'))
    else:
        return dict(login_url=url_for('index'))


def inject_media_version():
    """Injects a media version for easy cache invalidation into templates""" 
    return dict(version=app.config.get('MEDIA_VERSION'))

def add():
    app.context_processor(inject_user)
    app.context_processor(inject_media_version)
