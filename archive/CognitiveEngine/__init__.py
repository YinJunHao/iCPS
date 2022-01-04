'''
This section is not needed because the flask app is created in the main run outside of all folders.
Unless a new flask app is created within this cognitive engine folder.
'''


# initialize secret key and CSRF


def create_app(secret_key, debug = True, async_mode = "eventlet"):
    # import blueprints
    from archive.CognitiveEngine.blueprints.job_execution.routes import job_execution
    from archive.CognitiveEngine.blueprints.process_flow_control.routes import process_flow_control

    # register blueprints
    app.register_blueprint(job_execution)
    app.register_blueprint(process_flow_control)
    csrf.exempt(job_execution)
    csrf.exempt(process_flow_control)

    return app