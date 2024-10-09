import os

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['DB_HOST'] = os.getenv("MYSQL_HOST")
    app.config['DB_USER'] = os.getenv("MYSQL_USER")
    app.config['DB_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
    app.config['DB_NAME'] = os.getenv("MYSQL_DATABASE")
    app.secret_key = os.getenv("SECRET_KEY")

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import survey
    app.register_blueprint(survey.bp)
    app.add_url_rule('/', endpoint='survey')

    from . import results
    app.register_blueprint(results.bp)
    app.add_url_rule('/', endpoint='results')

    return app