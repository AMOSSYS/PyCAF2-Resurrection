#!/usr/bin/python
# coding: utf8

import os
import datetime
import argparse
import shutil
import argcomplete
import traceback
import sys
import configparser
import pickle
import tempfile

from IPython import embed

if sys.version_info[0] < 3:
    print("This version of PyCAF is only compatible with Python3.")
    sys.exit(42)

from pycaf2.lib.extract import Extract, ExtractionFail
from pycaf2.lib.system import System
from pycaf2.lib import Logger


def setup_logger(server_archive, overwrite=False):
    """
    Setup Logger.
    Returns a tupple containing the Logger and the log_name
    TODO: Adapt this for PyCAF-web !
    """

    # Log name should be the same as the archive
    # log_name = "{}.log".format(os.path.split(server_archive)[1])
    log_name = "output.log" # also hardcoded in Logger.py
    if os.path.exists(log_name):
        #Log file already exist, warn user and exit
        error = "Log file {} already exist.".format(log_name)
        if overwrite:
            print("{} Removing it.".format(error))
            os.remove(log_name)
        else:
            raise Exception(error)

    logger = Logger.getLogger(__name__)

    # Does not work for now
    # Create file handler to log into specific file at each iteration
    #fileHandler = logging.FileHandler(filename=log_name)
    #fileHandler.setLevel(logging.INFO)
    #fileHandler.setFormatter(logging.Formatter(fmt='%(message)s'))
    #logger.addHandler(fileHandler)

    return (logger, log_name)


def launch_pycaf(server_archive, config_file=None, interactive=False, pickler=False, overwrite=False):
    # Process input file

    if not os.path.exists(server_archive):
        error = "Server_archive or folder {} does not exist".format(server_archive)
        raise Exception(error)

    # Clear ending slash if any
    if server_archive[-1] == '/':
        server_archive = server_archive[:-1]

    # Initialize loggerversion
    (logger, log_name) = setup_logger(server_archive, overwrite)
    # Load required classes
    extractor = Extract()
    system = System()

    #filename = os.path.split(server_archive)
    filename = server_archive
    logger.debug("Filename is: {}".format(filename))

    clean = True

    # Check if user wants to analyze a directory or an archive
    have_to_extract = True

    # Print title with filename and datetime
    now = datetime.datetime.now()
    if os.path.isdir(filename):
        title = "Analyzing {} ({})".format(filename, now.strftime("%Y-%m-%d %H:%M"))
        logger.debug("Detected that dumpfile is a directory.")
        have_to_extract = False
        clean = False
    else:
        title = "{} ({})".format(os.path.split(server_archive)[1], now.strftime("%Y-%m-%d %H:%M"))

    logger.info(title)

    try:
        try:
            server = extractor.load_file(server_archive, have_to_extract)
        except ExtractionFail:
            error = "Extraction has failed"
            raise Exception(error)

        # Deal with arguments if anything mandatory
        os_detection = True
        if config_file is not None:
            if not os.path.exists(config_file):
                raise Exception("File {} does not exist".format(config_file))

            logger.info("Reading server configuration from: {}".format(config_file))
            config = configparser.ConfigParser()
            config.read(config_file)
            if 'server' not in config:
                raise Exception("Configuration file does not have a server section, checkout server.conf example.")

            os_detection = False
            if 'system_type' in config['server']:
                logger.info("Force OS to: {}".format(config['server']['system_type']))
                server.os_informations["system_type"] = config['server']['system_type']

            if server.os_informations["system_type"] == "linux":
                if 'os' not in config['server'] or 'code_name' not in config['server'] \
                or 'arch' not in config['server'] or 'distribution' not in config['server']:
                    raise Exception("Missing elements in configuration file, checkout server.conf example.")

                logger.info("Force OS to {}".format(config['server']['os']))
                server.os_informations["os"] = config['server']['os']

                logger.info("Force code_name to {}".format(config['server']['code_name']))
                server.os_informations["code_name"] = config['server']['code_name']

                logger.info("Force arch to {}".format(config['server']['arch']))
                server.os_informations["arch"] = config['server']['arch']

                logger.info("Force specific distribution to {}".format(config['server']['distribution']))
                server.os_informations["distribution"] = config['server']['distribution']

            if server.os_informations["system_type"] == "windows":
                if 'os' not in config['server'] or 'version' not in config['server'] \
                or 'arch' not in config['server']:
                    raise Exception("Missing elements in configuration file, checkout server.conf example.")

                logger.info("Force OS to {}".format(config['server']['os']))
                server.os_informations["os"] = config['server']['os']

                logger.info("Force version to {}".format(config['server']['version']))
                server.os_informations["version"] = config['server']['version']

                logger.info("Force arch to {}".format(config['server']['arch']))
                server.os_informations["arch"] = config['server']['arch']

        if os_detection:
            # Try to detect OS information.
            # Raise exception if system is not identified.
            title = "OS dump informations"
            logger.debug(title)
            try:
                server.os_informations = system.os_identifier(server)
            except Exception as e: #OsIdentifierException:
                logger.error("Error : %s " % e)
                raise Exception("OS cannot be identified. Use parameters to force one.")

            logger.debug("Detection results for UUID: {}".format(server.uuid))

            for key, value in server.os_informations.items():
                logger.debug("{}: {}".format(key.capitalize().replace("_", " "), value))

        # Process Server
        logger.debug("Analyzing {} extracted archive...".format(server.os_informations["os"]))
        server.init_modules()
        for module in server.get_modules():
            title = "Loading module: %s" % module.name
            logger.debug(title)
            try:
                logger.info("\n## {}".format(module.name))
                module.run(server)
                module.print_res()
            except Exception as e:
                tb = traceback.format_exc()
                logger.error("Module crashed: {}".format(tb))

        logger.debug("Analysis of {} is finished. Checkout log {} for the report."
                        .format(server_archive, log_name))


        if interactive == True:
            logger.debug("Starting interactive ipython. You can now interact with" +
            "server and analysis modules.")
            embed()

        # Pickle server if asked to
        if pickler:
            try:
                (fd, pickle_filename) = tempfile.mkstemp(prefix='pycaf_pickles_')
                with open(pickle_filename, 'wb') as f:
                    pickle.dump(server, f, pickle.HIGHEST_PROTOCOL)

                logger.info("Server object has been pickled in {}".format(pickle_filename))

            except pickle.PickleError as e:
                logger.error("Pickle error: {}".format(e))


    except Exception:
        tb = traceback.format_exc()
        logger.error("Error: {}".format(tb))

    finally:
        if clean is True:
            if server and server.extracted_folder:
                if os.path.exists(server.extracted_folder):
                    logger.debug("Cleaning directory: {}".format(server.extracted_folder))
                    shutil.rmtree(server.extracted_folder)
        if pickler:
            return pickle_filename
        return None
