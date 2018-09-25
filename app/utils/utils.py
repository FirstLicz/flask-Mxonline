def createsuperuser():
    from app.models import User, Role
    from app import db
    Role.insert_roles()
    user = input("please input super user:")
    result = User.query.filter_by(username=user).first()
    while result:
        user = input("please input again:")
        result = User.query.filter_by(username=user).first()
    passwd = input("please input password:")
    u = User()
    u.username = user
    u.name = user
    u.confirmed = True
    role = Role.query.filter_by(name='Administrator').first()
    u.role = role
    u.password = passwd
    db.session.add(u)
    db.session.commit()
