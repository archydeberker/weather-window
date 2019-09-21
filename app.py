from flask import Flask
from models import db
from routes import api


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.register_blueprint(api)

    db.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=True, host="127.0.0.1", port=5000
    )  # run app in debug mode on port 5000