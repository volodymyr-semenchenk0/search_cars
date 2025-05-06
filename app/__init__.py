import os

from flask import Flask

from .routes import register_routes


def create_app():
    # шлях до самого this file (app/__init__.py)
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # збираємо абсолютні шляхи до templates/ та static/
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    register_routes(app)

    return app
