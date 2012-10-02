#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, Cabo Communications A/S
# All rights reserved.
#
import datetime
import logging
import urllib

import sqlalchemy
from flask import request, render_template, redirect, flash, abort, Response, session, url_for, g

from decorators import login_required

import mail

from forms.login import LoginForm
from forms.job import JobForm
from forms.user import UserForm
import server

from app import app
config = app.config

from models import User, ValidationTokens, Job, db

import context_processors 
context_processors.add() # injects users

PASSWORD_RECOVERY_VALIDITY = datetime.timedelta(days=2)
DEBUG = config.get('DEBUG')

ALLOWED_EMAILS = ['jakob.a.dam@gmail.com', 'jmahle4u@gmail.com']
ALLOWED_DOMAINS = ['cs.au.dk', 'egaa-gym.dk', 'cabo.dk', 'niels.brock.dk', 'eg-gym.dk']

@app.template_filter('truncate')
def truncate_filter(value, length=50):
    if len(value) > length:
        return value[:length] + '...'
    return value

@app.before_request
def before_request():
    """Populates the global g object with the user if session['username'] is there"""
    username = session.get('username')
    if username:
        u = User.query.filter_by(email=username).first()
        if u is not None:
            g.user = u
            return
    g.user = None

####################
# Standard 404 page
###################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

##########
# handlers
##########
@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user:
        r = Response(render_template('home.html'))
        r.headers['Cache-Control'] = 'no-cache'
        return r
    else:
        return login()

@app.route('/logout/', methods=['GET'])
def logout():
    if g.user:
        del session['username']
        flash("Du er nu logget ud", 'message')
    return redirect(url_for('index'), 302)

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = UserForm(request.form)
    
    if not form.validate_on_submit():
        return render_template('signup.html', form=form)

    user = User()
    form.populate_obj(user)
    passwd = form.password.data # un-encrypted
    
    if not user.email in ALLOWED_EMAILS and not user.email.split('@')[1] in ALLOWED_DOMAINS:
        flash(u"Desværre - du skal have en email fra et godkendt uddannelsessted", 'error')
        return render_template('signup.html', form=form)

    token = ValidationTokens(user=user, 
                             type=ValidationTokens.CREATE_USER,
                             password=passwd)

    db.session.add(user)
    db.session.add(token)

    db.session.commit()
    
    link = '%s?token=%s' % (url_for(verify.__name__, _external=True), token.token)
    msg = render_template('email_verification.txt', user=user, link=link)

    mail.send(receivers=[u'%s <%s>' % (user.username, user.email)], 
              subject=u'Bekræft din email adresse til Iftek-skyen', 
              text=msg)

    flash(u"""Fedt, du er blevet oprettet!<br /><br />
For at aktivere din konto, skal du bekræfte din email adresse.<br /><br />
Vi har sendt en email med et link<br /><br />
Ses snart i skyen!""")

    return redirect(url_for(flash_message.__name__))

def login():
    if g.user:
        return redirect('/')

    form = LoginForm(request.form)
    users = User.query.all()
    if not form.validate_on_submit():
        logging.info('login form did not validate: %s' % form.errors)
        return render_template('login.html', 
                               users=users,
                               form=form,
                               signuplink=url_for('signup'))
    else:
        email = form.email.data
        session['username'] = email

        response = redirect(request.args.get('continue', request.script_root))

        flash("Du er nu logget ind!", 'message')
        return response

@app.route('/verify-email/')
def verify():
    token_key = request.args.get('token')
    token = ValidationTokens.query.filter_by(token=token_key)
    if token:
        token = token[0]
        user = token.user
        token.user.status = User.STATUS_ACTIVE

        db.session.add(user)

        server.user_create( user.username, passwd=token.password)
        dbname = "%s.%s" % (user.username, 'blog')
    
        server.db_create_user(user.username, token.password)
        server.db_create_database(dbname, user.username)

        sql = render_template('sql/blog.sql')
        server.db_execute(dbname, user.username, token.password, sql)

        db.session.delete(token)
        db.session.commit()

        session['username'] = user.email

        flash("Sejt, din konto er nu aktiveret.")
    else:
        flash(u"Ups, email verifikationen fejlede. Måske har du allerede " +
              "aktiveret denne konto", 'error')
    return redirect(request.script_root)

@app.route('/reset-password/', methods=['GET', 'POST'])
def reset_password():
    try:
        del session['username']
    except KeyError:
        pass

    g.user = None

    token = request.args.get('token')
    now = datetime.datetime.now()

    if token:
        try:
            token = ValidationTokens.query.filter_by(token=token).one()
        except sqlalchemy.orm.exc.NoResultFound:
            flash(u"Beklager, kunne ikke nulstille kodeordet. Linket kan kun bruges en gang", 'error')
            return redirect(request.script_root, 302)

        if token.created + PASSWORD_RECOVERY_VALIDITY < now:
            flash(u"Beklager, linket er udløbet.",
                  'error')
            return redirect(request.script_root, 302)

        form = forms.resetpassword.VerifiedResetForm(request.form)
        if form.validate_on_submit():
            token.user.password = form.password.data
            db.session.add(token.user)
            db.session.delete(token)
            db.session.commit()
            session['username'] = token.user.email
            flash('Dit kodeord blev nulstillet!')
            return redirect('/', 303)
        else:
            return render_template('reset-password.html',
                                   form=form)

    form = forms.resetpassword.RequestResetForm(request.form)
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).one()

        try:
            token = ValidationTokens(user=user,
                                     type=ValidationTokens.CREATE_USER)
            db.session.add(token)
            db.session.commit()
        except:
            db.session.delete(token)
            db.session.commit()
            raise

        link = (url_for('reset_password', _external=True) +
                '?token=' + token.token)

        msg = render_template('reset-password.txt', user=user,
                              link=link)

        mail.send(receivers=[u'%s <%s>' % (user.username, user.email)],
                  subject='Password Reset',
                  text=msg)

        flash("We've sent a mail to your account! Please click the link " +
              "in the message to reset your password.")

        return redirect('/')
    else:
        return render_template('reset-password.html', form=form)

@app.route('/message/')
def flash_message():
    """Renders an empty page showing flashed message"""
    message = request.args.get('message')
    error = request.args.get('error')
    if message:
        flash(urllib.unquote(message))
    if error:
        flash(urllib.unquote(error), 'error')
    if message or error:
        return redirect(url_for(flash_message.__name__))
    return render_template('flash_message.html')

@app.route('/jobs/', methods=['GET', 'POST'])
@login_required
def jobs():
    form = JobForm(request.form)
    if form.validate_on_submit():
        job = Job(user=g.user)
        form.populate_obj(job)
        db.session.add(job)
        db.session.commit()
        flash('Nyt job oprettet')
        return redirect(url_for('jobs'))
    return render_template('jobs.html', jobs=g.user.jobs.all(), form=form)

@app.route('/jobs/<id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_job(id):
    job = Job.query.get_or_404(id)
    if job.user != g.user:
        return abort(404)
    db.session.delete(job)
    db.session.commit()
    flash('Job slettet!')
    return redirect(url_for('jobs'))

if __name__ == '__main__':
    db.create_all()
    app.run(host='')
