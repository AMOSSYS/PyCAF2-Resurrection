#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, shutil, os

from pycaf_web.app import create_app

print("PATH={}".format(sys.path))

app = create_app()

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            print("Removing upload folder: {}".format(app.config['UPLOAD_FOLDER']))
            shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)

        if app.config['PICKLED_FILES']:
            for pickled_file in app.config['PICKLED_FILES']:
                if os.path.exists(pickled_file):
                    print("Removing pickled_file: {}".format(pickled_file))
                    os.remove(pickled_file)
