def run():
    import server
    from models import User,db

    result = []

    def fail(e):
        result.append(' FAIL<br>')
        result.append(str(e))
        result.append('<br>')

    def ok():
        result.append(' OK<br>')


    try:
        result.append('Test sudo cat')
        server.sudo('cat /tmp/foo')
        ok()
    except Exception,e:
        fail(e)

    from models import DomainWhitelist, Whitelist

    try:
        result.append('Test domain whitelist')
        d = DomainWhitelist(domain='example.com')

        db.session.add(d)
        db.session.commit()

        if Whitelist.allowed('jakob@example.com'):
            ok()
        else:
            fail("Wasn't whitelisted")

        db.session.delete(d)
        db.session.commit()

    except Exception, e:
        fail(e)

    try:
        result.append('Test user create')
        user = User(email='jakob@example.com', username='foobar', password=u'foobar') 
        User.useradd('foobar', 'foobar')
        db.session.add(user)
        db.session.commit()
        ok()
    except Exception,e:
        fail(e)

    try:
        result.append('Test username replace in config.php')
        with open('/home/foobar/public_html/blog/conf/config.php') as f:
            s = f.read()
            if 'dit_brugernavn' in s:
                fail("not replaced")
            else:
                ok()
    except Exception, e:
        fail(e)

    try:
        result.append('Test user delete')
        User.userdel('foobar')
        ok()
    except Exception, e:
        fail(e)

    return ''.join(result)
