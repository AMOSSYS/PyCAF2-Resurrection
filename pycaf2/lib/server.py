# -*- coding: utf8 -*-

import glob
import os
import importlib
import traceback
import uuid

from pycaf2.lib import Logger

class Server(object):

    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.extracted_folder = None
        self.file_list = None
        self.modules = [] # Loaded modules
        self.os_informations = dict()
        """ os_informations structure has the following format:
        * for Linux
            {"score": score,
                "data": {
                    "system_type": "linux|windows",
                    "os": "debian|centos|generic",
                    "kernel": kernel,
                    "version": version,
                    "arch": "x86|x64"
                }
            }
        * for Windows:
                "data": {
                    "system_type": "windows",
                    "os": "Microsoft Windows Server 2012 R2 Standard | Microsoft Windows Server 2008 R2 Enterprise | ...",
                    "version": "6.1.7601 Service Pack 1 Build 7601",
                    "arch": "x64-based PC" ## TODO: this will cause problem...
                } """

    def init_modules(self):
        """ Load all modules from system name
        """
        if "system_type" not in self.os_informations:
            raise Exception("System type has not been initialized, cannot load any module.")
        if "os" not in self.os_informations:
            raise Exception("System OS has not been initialized, cannot load any module.")

        logger = Logger.getLogger(__name__)

        modules_list = []
        logger.debug("Loading available modules for system: {}".format(self.os_informations["system_type"]))

        ## Load system modules
        modules_path = os.path.join("pycaf2", "modules")
        files = glob.glob(os.path.join(modules_path, self.os_informations["system_type"], self.os_informations["os"], "*"))
        # Add generic modules
        if self.os_informations["os"] != "generic":
            files += glob.glob(os.path.join(modules_path, self.os_informations["system_type"], "generic", "*"))

        if not files:
            logger.error("Cannot find any modules to import, checkout modules' path: {}".format(modules_path))

        classes_loaded = []
        for afile in files:
            file_name, file_extension = os.path.splitext(afile)
            if not file_name.endswith("__init__") and file_extension == ".py":
                #logger.debug("Found: {}".format(file_name))
                module_name = file_name.replace(os.path.sep, ".")
                logger.debug("Module name is: {}".format(module_name))

                class_name = module_name.split(".")[-1]

                try:
                    # Do not load generic module when dedicated one has been already loaded
                    if class_name not in classes_loaded:
                        mod = importlib.import_module(module_name)
                        #logger.debug("Import module succeeded")
                        mod_class = getattr(mod, class_name)
                        modules_list.append(mod_class())
                        classes_loaded.append(class_name)
                    else:
                        pass #logger.debug("Do not load module: {}".format(module_name))

                except Exception:
                    tb = traceback.format_exc()
                    logger.error("Cannot load module {}: {}".format(module_name, tb))

        self.modules = modules_list

    def get_modules(self):
        return self.modules


    def get_module(self, module_name):
        for module in self.modules:
            if module.name == module_name:
                return module
        return None
