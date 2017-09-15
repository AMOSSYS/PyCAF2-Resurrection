#!/usr/bin/python
# -*- coding: utf8 -*-

import unittest
import os
import pickle

from pycaf2.lib import Logger
from pycaf2.lib.extract import Extract, ExtractionFail

class TestServerMethods (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)

        #import dump folder and file_list
        extractor = Extract()
        try:
            self.server = extractor.load_file(os.path.join("pycaf2", "test", "resources", "linux", "HPLWEBFR1-01"), False)
        except ExtractionFail:
            raise Exception("Extraction Failed.")

    def tearDown(self):
        pass

    def test_server(self):
        """
        Tests that Server correctly load file and that get_modules function returns
        a not empty array, with a first element.
        """
        self.logger.info("Testing Server...")
        # set os_informations[os] to debian
        self.server.os_informations["system_type"] = "linux"
        self.server.os_informations["os"] = "centos"

        self.server.init_modules()
        modules = self.server.get_modules()

        self.assertIsNotNone(len(modules))
        # Concat names of existing modules
        names = []
        for module in modules:
            names.append(module.name)
        self.assertIn("Accounts", names)

        # test pickling
        try:
            pickle_filename = "server.pickle"
            with open(pickle_filename, 'wb') as f:
                pickle.dump(self.server, f, pickle.HIGHEST_PROTOCOL)

            self.logger.debug("Server object has been pickled in {}".format(pickle_filename))
            self.logger.debug("Now trying to unpickle...")
            with open(pickle_filename, 'rb') as f:
                server_unpickled = pickle.load(f)

            self.logger.debug("Server has been unpickled! Accessing os: {}".format(server_unpickled.os_informations["os"]))
            self.assertEqual(server_unpickled.os_informations["os"], "centos")

        except pickle.PickleError as e:
            self.logger.error("Pickle error: {}".format(e))


    def test_compare_servers(self):
        self.logger.info("Testing comparing 2 pickled servers...")

        server1_path = os.path.join("pycaf2", "test", "resources", "linux", "pickle", "server1.pickle")
        if not os.path.exists(server1_path):
            raise Exception("Path {} does not exist.".format(server1_path))

        server2_path = os.path.join("pycaf2", "test", "resources", "linux", "pickle", "server2.pickle")
        if not os.path.exists(server2_path):
            raise Exception("Path {} does not exist.".format(server2_path))

        with open(server1_path, 'rb') as f:
            server1 = pickle.load(f)
        self.logger.debug("Server1 has been unpickled")

        with open(server2_path, 'rb') as f:
            server2 = pickle.load(f)
        self.logger.debug("Server2 has been unpickled")

        self.logger.debug("Now trying to compare them.")

        # Sort modules
        module_names1 = sorted([x.name for x in server1.get_modules()])
        module_names2 = sorted([x.name for x in server2.get_modules()])

        # Check if servers have the same modules
        s = set(module_names2)
        res = [x for x in module_names1 if x not in s]
        if res:
            self.logger.error("Found modules {} which are different between the 2 servers".format(res))
        else:
            self.logger.info("Servers have the same modules, now checking results...")

            # For each module of server1 and server2, check infos, improvements, warnings and errors
            for module_name in module_names1:
                self.logger.debug("Checking module: {}...".format(module_name))
                module1 = server1.get_module(module_name)
                module2 = server2.get_module(module_name)

                self.compare_module(module1, module2)


    def compare_module(self, module1, module2):
        # Compare infos
        res = self.get_diff(module1.get_infos(), module2.get_infos())
        if res:
            self.logger.error(" /!\ Found infos that are different between the 2 servers.")
            for _index in res:
                self.logger.error("\tServer1: {}".format(module1.get_infos()[_index]))
                self.logger.error("\tServer2: {}".format(module2.get_infos()[_index]))
        else:
            self.logger.info(" + Modules have the same infos")

        # Compare improvements
        res = self.get_diff(module1.get_improvements(), module2.get_improvements())
        if res:
            self.logger.error(" /!\ Found improvements that are different between the 2 servers.")
            for _index in res:
                self.logger.error("\tServer1: {}".format(module1.get_improvements()[_index]))
                self.logger.error("\tServer2: {}".format(module2.get_improvements()[_index]))
        else:
            self.logger.info(" + Modules have the same improvements")


        # Compare warnings
        res = self.get_diff(module1.get_warnings(), module2.get_warnings())
        if res:
            self.logger.error(" /!\ Found warnings that are different between the 2 servers.")
            for _index in res:
                self.logger.error("\tServer1: {}".format(module1.get_warnings()[_index]))
                self.logger.error("\tServer2: {}".format(module2.get_warnings()[_index]))
        else:
            self.logger.info(" + Modules have the same warnings")

        # Compare criticals
        res = self.get_diff(module1.get_criticals(), module2.get_criticals())
        if res:
            self.logger.error(" /!\ Found criticals that are different between the 2 servers.")
            for _index in res:
                self.logger.error("\tServer1: {}".format(module1.get_criticals()[_index]))
                self.logger.error("\tServer2: {}".format(module2.get_criticals()[_index]))
        else:
            self.logger.info(" + Modules have the same criticals")


    def get_diff(self, module1, module2):
        s = set(module1)
        #res = [x for x in module2.get_infos() if x not in s]
        res = dict()
        index = 0
        for info in module2:
            if info not in s:
                res[index] = info
            index=index+1
        return res
