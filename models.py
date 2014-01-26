# -*- coding: utf-8 -*-

#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import DateTime
from sqlalchemy import func

import uuid

from flask.ext.sqlalchemy import SQLAlchemy
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

class Whitelist(object):

    @classmethod
    def allowed(cls, email):
        if EmailWhitelist.allowed(email):
            return True
        if DomainWhitelist.allowed(email):
            return True
        return False

class DomainWhitelist(db.Model):

    __table_args__ = {'mysql_engine':'InnoDB'}
    __tablename__ = 'domain_whitelist'

    domain = Column(String(255), primary_key=True)

    @classmethod
    def allowed(cls, email):
        domain = email.split('@')[1]
        u = DomainWhitelist.query.filter_by(domain=domain).first()
        if u:
            return True
        return False

class EmailWhitelist(db.Model):

    __table_args__ = {'mysql_engine':'InnoDB'}
    __tablename__ = 'email_whitelist'

    email = Column(String(255), primary_key=True)

    @classmethod
    def allowed(cls, email):
        u = EmailWhitelist.query.filter_by(email=email).first()
        if u:
            return True
        return False

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

    @classmethod
    def userdel(cls, username):
        import server

        # remove user from server
        server.user_remove(username)

        # remove user's database
        sql = "DROP USER %s; DROP DATABASE `%s.blog`; DELETE FROM skyen.users WHERE username = '%s';" % (username, username, username)
        db.engine.execute(sql)

        # # remove user from skyen db
        # u = User.query.filter_by(username=username).first()
        # db.session.delete(u)
        # db.session.commit()

    @classmethod
    def useradd(cls, username, password):
        import server
        from flask import render_template

        server.user_create( username, passwd=password)
        dbname = "%s.%s" % (username, 'blog')

        server.db_create_user(username, password)
        server.db_create_database(dbname, username)

        sql = render_template('sql/blog.sql')
        server.db_execute(dbname, username, password, sql)

        # set username password in blog
        config_path = '/home/%s/public_html/blog/conf/config.php' % username
        config = None

        with open(config_path, 'rb') as f:
            config = unicode(f.read(), "utf-8")

        config = config.replace('dit_brugernavn', username)
        config = config.replace('dit_password', password)

        with open(config_path,'wb') as f:
            f.write(config.encode("utf-8"))

class ValidationTokens(db.Model, Model):

    __tablename__ = u'validation_tokens'

    CREATE_USER = 'create_user'
    RESET_PASSWORD = 'password_reset'

    TYPES = (CREATE_USER, RESET_PASSWORD)

    token = Column(String(32), nullable=False, default=lambda: uuid.uuid4().hex)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(Enum(*TYPES), nullable=False)
    password = Column(String(32))

    def __unicode__(self):
        return self.token.decode('ascii')

class Job(db.Model, Model):

    __tablename__ = u'jobs'

    url = Column(String(100), nullable=False)
    hour = Column(Integer, nullable=False)
    last_run = Column(DateTime)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('jobs', lazy='dynamic'))
