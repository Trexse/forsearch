from Notice import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = create_app("product")
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@manager.command
def create_admin():
    from Notice.modles import Admin
    from Notice.message import ADMIN_USERNAME, ADMIN_PASSWORD
    try:
        admin_new = Admin(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        db.session.add(admin_new)
        db.session.commit()
        print("初始化成功")
    except:
        print("初始化失败")
        db.session.rollback()


if __name__ == '__main__':
    manager.run()
