import os

from flask import Flask
from config import POSTGRES, BOTO3_CONFIG

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the instance folder
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),

        # Use Postgres from config file instead
        SQLALCHEMY_DATABASE_URI='postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        BOTO3_SERVICES=BOTO3_CONFIG['service'],
        BOTO3_ACCESS_KEY=BOTO3_CONFIG['access_key'],
        BOTO3_SECRET_KEY=BOTO3_CONFIG['secret_key'],
        BOTO3_REGION=BOTO3_CONFIG['region'],
    )
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flaskr import picture
    picture.init_boto(app)

    # register the database commands
    from flaskr import db
    db.init_app(app)

    # apply the blueprints to the app
    from flaskr import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule('/', endpoint='index')

    return app
