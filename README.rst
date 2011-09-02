==========
Iftek Pass
==========

Installation
============
To run control you must have the follow installed:

 * Python 2.6+
 * virtualenv 1.4.7+
 * Fabric 1.1.0

Setting up environment
----------------------

Create a virtual environment where control dependencies will live::

    $ virtualenv --no-site-packages iftek
    $ source {path_to_virtual_envs}/control/bin/activate
    (control)$

Install control project dependencies::

    (iftek)$ pip install -r conf/requirements_dev.txt

Deployment
----------
Iftek PaaS uses fabric to manage deployment. Specify the hostname of your
ubuntu server in fabfile.py and run

    $ fab setup

That command will setup apache, mysql, python, and
checkout the app to the server.

Running a local web server
--------------------------
In development you should run:

    (iftek)$ python paas.py

Working in the production environment
-------------------------------------

Before working with, e.g., the models in a Python session, the
settings must be specified.

    $ export SETTINGS=./conf/settings.cfg

Errors Notifications
--------------------

In production all error messages are emailed to the admins. Admins is a
list in ./conf/settings.cfg.

