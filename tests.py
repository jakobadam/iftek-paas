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
    # test create user

    try:
        result.append('Test sudo cat')
        s = server.sudo('cat /tmp/foo')
        ok()
    except Exception,e:
        fail(e)

    try:
        result.append('Test user create')
        user = User(email='foobar@example.com', username='foobar', password='foobar')
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
