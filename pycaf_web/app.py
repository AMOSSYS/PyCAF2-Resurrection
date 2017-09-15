#!/usr/bin/python
# -*- coding: utf8 -*-

import os, tempfile
from flask import Flask
from flask_bootstrap import Bootstrap

from pycaf_web.nav import nav
from pycaf_web.blueprints import main, servers


def create_app():
    app = Flask(__name__)
    print("Creating new app!")

    # Init bootstrap within Flask
    Bootstrap(app)

    # Init et setup navigation bar
    nav.init_app(app)
    # register blueprints
    register_blueprints(app)

    # Configure uploads
    ALLOWED_EXTENSIONS = set(['tar.gz', 'tar.xz', 'bz2', 'zip'])


    UPLOAD_FOLDER = tempfile.mkdtemp(prefix='pycaf_uploads_')
    print("Created upload folder: {}".format(UPLOAD_FOLDER))

    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['PICKLED_FILES'] = []
    # Necessary if we want to upload files
    app.secret_key = '3aw/e6FjKh5iI/xnMztGqRKw5Ylni2kIg8AMXdtq9Fo='

    return app


def register_blueprints(app):
    """
    Registers blueprints.
    """
    app.register_blueprint(main.views.blueprint)
    app.register_blueprint(servers.views.blueprint)
