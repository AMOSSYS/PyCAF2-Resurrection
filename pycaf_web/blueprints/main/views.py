#!/usr/bin/python
# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import current_app as app
from werkzeug.utils import secure_filename
import os

from pycaf_web.blueprints.servers.views import load_server, get_server_from_uuid
from pycaf2.pycaf import launch_pycaf

blueprint = Blueprint('main', __name__, template_folder='templates')

@blueprint.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')

@blueprint.route('/import_server')
def import_server():
    return render_template('main/import_server.html')

@blueprint.route('/run_pycaf', methods=['GET'])
def run_pycaf():
    # Render
    return render_template('main/pycaf_launcher.html')

@blueprint.route('/import_from_file', methods=['POST'])
def import_from_file():
    """
    Get pickled server from input form, save it in the upload folder and load
    server.
    CAREFUL: this function may be dangerous ==> unserialisation baby.
    """
    # Import server from file
    if "pickled_file" not in request.files:
        return "No pickled_file part in POST data"

    pickled_file = request.files['pickled_file']

    if not pickled_file:
        return "No selected file"
    if not pickled_file.filename:
        return "No selected file"

    filename = secure_filename(pickled_file.filename)
    file_path = os.path.join (app.config['UPLOAD_FOLDER'], filename)
    pickled_file.save(file_path)
    print("File has been uploaded here: {}".format(file_path))

    if not os.path.exists(file_path):
        return "Path {} does not exist.".format(file_path)
    print("Path: {}".format(file_path))

    uuid = load_server(file_path)
    return redirect( url_for('servers.get_server_from_uuid', uuid=uuid) )


@blueprint.route('/import_and_run', methods=['POST'])
def import_and_run():
    """
    Get archive from input form, save it in the upload folder and run PyCAF.
    Redirect user on server details.
    """
    if "archive" not in request.files:
        return "No archive part in POST data"

    archive_file = request.files['archive']

    if archive_file.filename == '':
        return "No selected file"

    if allowed_file(archive_file.filename):
        filename = secure_filename(archive_file.filename)

        file_path = os.path.join (app.config['UPLOAD_FOLDER'], filename)
        archive_file.save(file_path)
        print("File has been uploaded here: {}".format(file_path))

        if not os.path.exists(file_path):
            return "Path {} does not exist.".format(file_path)

        # Run PyCAF !
        pickled_file = launch_pycaf(file_path, config_file=None, interactive=False, pickler=True, overwrite=True)
        if pickled_file:
            uuid = load_server(pickled_file)
            app.config['PICKLED_FILES'].append(pickled_file)
            return redirect( url_for('servers.get_server_from_uuid', uuid=uuid) )

        return "PyCAF analyzer has returned None, checkout debug logs."
    else:
        return "File extension is not allowed."


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
