# -*- coding: utf-8 -*-

#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#
import logging

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.sql.expression import desc
# from sqlalchemy import UniqueConstraint
# from flaskext.sqlalchemy import models_committed
from random import sample
from random import randrange

from sqlalchemy import DateTime, Date
from sqlalchemy import func

from datetime import date
from datetime import timedelta
from datetime import datetime

import uuid

from flaskext.sqlalchemy import SQLAlchemy
from flask import url_for

from app import app

db = SQLAlchemy(app)

class ModelError(Exception):
    pass

class Model(object):

    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.current_timestamp())
    updated = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __init__(self, **kwargs):
        [setattr(self, k, v) for k,v in kwargs.iteritems()]
        
    def put(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def is_saved(self):
        return self.id != None

    @classmethod
    def get_or_insert(cls, id, **kwargs):
        instance = cls.query.get(id)
        if instance is None:
            instance = cls(id=id, **kwargs)
            instance.put()
        return instance

class Auth(Model):

    _password = Column('password', String(255), nullable=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = Auth.get_password(password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        salt, hsh = self.password.split('$')
        return hsh == Auth.get_hexdigest(salt, raw_password)

    @staticmethod
    def get_password(raw_password):
        import random
        salt = Auth.get_hexdigest(str(random.random()), str(random.random()))[:5]
        hsh = Auth.get_hexdigest(salt, raw_password)
        return '%s$%s' % (salt, hsh)

    @staticmethod
    def get_hexdigest(salt, raw_password):
        import hashlib
        return hashlib.sha1(salt + raw_password).hexdigest()

class User(db.Model, Auth):

    __tablename__ = u'users'

    STATUS_NEW = 'new'
    STATUS_ACTIVE = 'active'
    STATUS_LOCKED = 'locked'

    STATUSES = (STATUS_NEW, STATUS_ACTIVE, STATUS_LOCKED)

    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    is_staff = Column(Boolean(), nullable=False, default=False)
    status = Column(Enum(*STATUSES), default=STATUS_NEW)

    # messages
    # services
    tokens = relationship('ValidationTokens', backref='user')

    @property
    def url(self):
        return url_for('edit_user')

    @property
    def is_admin(self):
        return self.email in app.config.get('ADMINS')

class ValidationTokens(db.Model, Model):

    __tablename__ = u'validation_tokens'

    CREATE_USER = 'create_user'
    RESET_PASSWORD = 'password_reset'
    
    TYPES = (CREATE_USER, RESET_PASSWORD)

    token = Column(String(32), nullable=False, default=lambda: uuid.uuid4().hex)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(Enum(*TYPES), nullable=False)

    def __unicode__(self):
        return self.token.decode('ascii')
