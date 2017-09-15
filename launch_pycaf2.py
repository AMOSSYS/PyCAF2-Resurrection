#!/usr/bin/python
# coding: utf8

import os
import datetime
import argparse
import argcomplete

from pycaf2 import pycaf

if __name__ == "__main__":

    # Load module first so we can check what module to accept on the command line
    modules_list = os.listdir(os.path.join("pycaf2", "modules"))
    modules_list_directories = [folder for folder in modules_list if not '.' in folder]

    parser = argparse.ArgumentParser(description='PyCAF2 - Codename Resurrection')
    parser.add_argument('-f', '--file',
                        action='store',
                        dest='file',
                        required=True,
                        help='dump file (ex : dump1.tar.bz2). Specify a folder if you want to skip the extraction.')
    parser.add_argument('--config_file',
                        action='store',
                        dest='config_file',
                        default=None,
                        help='path to the configuration file (see server.conf for example)')
    parser.add_argument('-i', '--interactive',
                        action='store_true',
                        help='start interactive ipython console after PyCAF work')
    parser.add_argument('-s', '--pickle-to',
                        action='store_true',
                        dest='pickler',
                        help='store server object into pickle file \'server.pickle\'')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    server_archive = args.file
    config_file = args.config_file
    interactive = args.interactive
    pickler = args.pickler
    # Launch parser
    pycaf.launch_pycaf(server_archive, config_file, interactive, pickler)
