import server
from models import DomainWhitelist, Whitelist
from models import User,db


def test_whitelist():
    d = DomainWhitelist(domain='example.com')

    db.session.add(d)
    db.session.commit()

    if not Whitelist.allowed('jakob@example.com'):
        raise Exception("Wasn't whitelisted")

    db.session.delete(d)
    db.session.commit()

def test_sudo_cat():
    server.sudo('cat /tmp/foo')

def test_user_create():
    user = User(email='jakob@example.com', username='foobar', password=u'foobar')
    User.useradd('foobar', 'foobar')
    db.session.add(user)
    db.session.commit()

def test_username_replace():
    with open('/home/foobar/public_html/blog/conf/config.php') as f:
        s = f.read()
        if 'dit_brugernavn' in s:
            raise Exception("not replaced")

def test_set_password():
    user = User.query.filter_by(username='foobar').first()
    user.set_password('foobarbaz')

def test_user_delete():
    User.userdel('foobar')

result = []

def fail(e):
    result.append(' FAIL<br>')
    result.append(str(e))
    result.append('<br>')

def ok():
    result.append(' OK<br>')

def run(f):
    try:
        result.append('Test %s' % f.__name__)
        f()
        ok()
    except Exception, e:
        fail(e)

def run_tests():
    global result
    result = []
    run(test_whitelist)
    run(test_sudo_cat)
    run(test_user_create)
    run(test_username_replace)
    run(test_set_password)
    run(test_user_delete)
    return ''.join(result)
