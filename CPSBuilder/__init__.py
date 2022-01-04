import config

from flask import Flask
from flask_wtf import CSRFProtect
# initialize secret key and CSRF

from CPSBuilder.modules.socketio import socketio


def create_app(debug=True, async_mode="eventlet"):
    app = Flask(__name__, static_folder="user_interface/layout/static", template_folder="user_interface/layout/templates")
    app.config['SECRET_KEY'] = config.secret_key
    app.config['excel_dir'] = config.excel_dir
    app.debug = debug
    csrf = CSRFProtect(app)

    #import blueprints
    from CPSBuilder.user_interface.blueprints.main.routes import main
    from CPSBuilder.user_interface.blueprints.user.routes import user
    from CPSBuilder.user_interface.blueprints.start.routes import start

    from CPSBuilder.user_interface.blueprints.resources.routes import resources
    # from CPSBuilder.user_interface.blueprints.new_resource.routes import new_resource
    # from CPSBuilder.user_interface.blueprints.remove_resource.routes import remove_resource
    # from CPSBuilder.user_interface.blueprints.edit_resource.routes import edit_resource

    from CPSBuilder.user_interface.blueprints.processes.routes import processes
    # from CPSBuilder.user_interface.blueprints.new_action.routes import new_action
    # from CPSBuilder.user_interface.blueprints.remove_action.routes import remove_action
    # from CPSBuilder.user_interface.blueprints.edit_definition.routes import edit_definition

    from CPSBuilder.user_interface.blueprints.history.routes import history
    from CPSBuilder.user_interface.blueprints.running.routes import running

    from CPSBuilder.user_interface.blueprints.ar.routes import ar

    from CPSBuilder.threads.blueprints.context.routes import context

    # register blueprints
    app.register_blueprint(main)
    app.register_blueprint(user)
    app.register_blueprint(start)
    app.register_blueprint(processes)
    app.register_blueprint(resources)
    # app.register_blueprint(new_resource)
    # app.register_blueprint(remove_resource)
    # app.register_blueprint(edit_resource)

    app.register_blueprint(history)
    app.register_blueprint(running)

    app.register_blueprint(context)

    app.register_blueprint(ar)
    # socketio must be at the last, like binding socketio to the app
    socketio.init_app(app, async_mode = async_mode)
    return app
