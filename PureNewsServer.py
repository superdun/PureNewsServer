
from app import create_app

application = create_app()
# manager = Manager(app)
# migrate = Migrate(app, models)
#
# def make_shell_context():
#     return dict(app=app, models=models)
#
# manager.add_command("shell", Shell(make_context=make_shell_context))
# manager.add_command("models", MigrateCommand)


if __name__ == '__main__':
    # manager.run()
    application.run(port=8080)