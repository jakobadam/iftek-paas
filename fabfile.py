import os

from fabric.api import env, cd, sudo, put, run, settings

env.hosts = ['193.200.45.133']
env.user = 'root'
env.root = "/srv/www/iftek-pass" # reflected in apache.conf and nginx.conf
env.activate = "source %(root)s/env/bin/activate" % env

def deploy():
    "Full deploy: push, update dependencies, and reload."
    push()
    update_dependencies()
    reload()
    
def push():
    "Push out new code to the server."
    with cd("%(root)s/app" % env):
        run("git pull")
        
def update_dependencies():
    "Update control requirements remotely."
    virtualenv("%(root)s/env/bin/pip install -r %(root)s/app/conf/requirements_prod.txt" % env)
        
def reload():
    "Reload Apache to pick up new code changes."
    run("invoke-rc.d apache2 reload")

def virtualenv(command):
    run(env.activate + ' && ' + command)

def elog():
    run("tail -f /var/log/apache2/error.log")

def log():
    run("tail -f /var/log/apache2/access.log")
    run("aptitude -y install ")

def setup_webserver():
    run("aptitude -y install "
        "apache2 "
        "apache2-mpm-worker "
        "libapache2-mod-wsgi "
        "webmin "
        "vsftpd "
        "mysql-server-5.1 "
        "python-dev "
        "python-setuptools "
        "libmysqlclient-dev "
        "git-core "
        )
    run("a2enmod userdir php5")
    run("cp %(root)s/app/conf/php5.conf /etc/apache2/mods-available" % env)
    run("mkdir -p /etc/skel/public_html")
    
def setup_app():
    run("mkdir -p %(root)s" % env)

    # make it possible to run user* stuff without password
    run("chmod 660 /etc/sudoers")
    run("rm /etc/sudoers")
    run("cp %(root)s/app/conf/sudoers /etc/sudoers" % env)
    run("chmod 220 /etc/sudoers")
    
    # create python virtualenv
    run("easy_install virtualenv")
    run("virtualenv %(root)s/env" % env)
    virtualenv("%(root)s/env/bin/pip install -U pip" % env)

    # Check out Control
    with cd("%(root)s" % env):
        run("git clone http://?")
    
def setup():
    """
    Set up (bootstrap) a new server.
    """
    # Initial setup and package install.
    run("aptitude update")
    setup_webserver()
    setup_app()

    deploy()

