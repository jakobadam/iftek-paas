import commands
import string
import random
import crypt
from app import app

from models import db

def run(command):
    error, output = commands.getstatusoutput("%s" % command)
    if error:
        raise Exception(output)
    return output

def sudo(command):
    return run("sudo %s" % command)

def db_execute(db, name, passwd, sql):
    sql = sql.replace('`', '\\`')
    cmd = """echo "%s" | mysql %s -u %s --password=%s""" % (sql, db, name, passwd)
    run(cmd)

# From: https://github.com/sebastien/cuisine/blob/master/src/cuisine.yp

# FIXME: validate username passwd in form

def db_set_password(username, passwd):
    sql = "SET PASSWORD FOR '%s'@'%%' = PASSWORD('%s')" % (username, passwd)
    db.session.execute(sql)

def db_create_user(username, passwd):
    sql = "CREATE USER '%s'@'%%' IDENTIFIED BY '%s';" % (username, passwd)
    db.session.execute(sql)

def db_create_database(dbname, username):
    stms = [
        "CREATE database `%s`;" % (dbname),
        "GRANT USAGE ON  *.* TO '%s'@'%%';" % (username),
        "GRANT ALL PRIVILEGES ON  `%s` . * TO  '%s'@'%%';" % (dbname, username)
    ]
    sql = ''.join(stms)
    db.session.execute(sql)

def user_remove(name, rmhome=None):
    """Removes the user with the given name, optionally
    removing the home directory and mail spool."""
    options = ["-f"]
    if rmhome:
        options.append("-r")
    sudo("/usr/sbin/userdel %s '%s'" % (" ".join(options), name))

def user_create( name, passwd=None, home=None, uid=None, gid=None, shell=None, uid_min=None, uid_max=None):
    """Creates the user with the given name, optionally giving a specific password/home/uid/gid/shell."""
    options = ["-m"]
    if passwd:
        method = 6
        saltchars = string.ascii_letters + string.digits + './'
        salt = ''.join([random.choice(saltchars) for x in range(8)])
        passwd_crypted = crypt.crypt(passwd, '$%s$%s' % (method, salt))
        options.append("-p '%s'" % (passwd_crypted))
    if home: options.append("-d '%s'" % (home))
    if uid:  options.append("-u '%s'" % (uid))
    if gid:  options.append("-g '%s'" % (gid))
    if shell: options.append("-s '%s'" % (shell))
    if uid_min:  options.append("-K UID_MIN='%s'" % (uid_min))
    if uid_max:  opitons.append("-K UID_MAX='%s'" % (uid_max))
    sudo("/usr/sbin/useradd %s '%s'" % (" ".join(options), name))

def user_check( name ):
    """Checks if there is a user defined with the given name, returning its information
    as a '{"name":<str>,"uid":<str>,"gid":<str>,"home":<str>,"shell":<str>}' or 'None' if
    the user does not exists."""
    d = sudo("cat /etc/passwd | egrep '^%s:' ; true" % (name))
    s = sudo("cat /etc/shadow | egrep '^%s:' | awk -F':' '{print $2}'" % (name))

    results = {}
    if d:
        d = d.split(":")
        results = dict(name=d[0],uid=d[2],gid=d[3],home=d[5],shell=d[6])
    if s:
        results['passwd']=s
    if results:
        return results
    else:
        return None

def user_ensure( name, passwd=None, home=None, uid=None, gid=None, shell=None):
    """Ensures that the given users exists, optionally updating their passwd/home/uid/gid/shell."""
    d = user_check(name)
    if not d:
        user_create(name, passwd, home, uid, gid, shell)
    else:
        options=[]
        if passwd != None and d.get('passwd') != None:
            method, salt = d.get('passwd').split('$')[1:3]
            passwd_crypted = crypt.crypt(passwd, '$%s$%s' % (method, salt))
            if passwd_crypted != d.get('passwd'):
                options.append("-p '%s'" % (passwd_crypted))
        if passwd != None and d.get('passwd') is None:
            # user doesn't have passwd
            method = 6
            saltchars = string.ascii_letters + string.digits + './'
            salt = ''.join([random.choice(saltchars) for x in range(8)])
            passwd_crypted = crypt.crypt(passwd, '$%s$%s' % (method, salt))
            options.append("-p '%s'" % (passwd_crypted))
        if home != None and d.get("home") != home:
            options.append("-d '%s'" % (home))
        if uid  != None and d.get("uid") != uid:
            options.append("-u '%s'" % (uid))
        if gid  != None and d.get("gid") != gid:
            options.append("-g '%s'" % (gid))
        if shell != None and d.get("shell") != shell:
            options.append("-s '%s'" % (shell))
        if options:
            sudo("/usr/sbin/usermod %s '%s'" % (" ".join(options), name))

if __name__ == '__main__':
    db_create_database('dbname', 'jakob')
    # print user_check('dam')
