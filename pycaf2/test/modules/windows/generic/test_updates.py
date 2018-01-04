#!/usr/bin/python3
# -*- coding: utf8 -*-

import unittest
import os

from pycaf2.lib import Logger
from pycaf2.modules.windows.generic import Updates

class TestUpdates (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)

        self.updates = Updates.Updates()

    # Windows test archives are not available anymore
    #def test_os_number(self):
    def old_os_number(self):
        self.logger.info("Testing Windows OS number...")

        # 5.2.3790 Service Pack 2 Build 3790, x64-based PC, Microsoft Windows Server 2003 Standard x64 Edition
        os_informations_2003 = dict()
        os_informations_2003["version"] = "5.2.3790 Service Pack 2 Build 3790"
        os_informations_2003["arch"] = "x64"
        os_informations_2003["os"] = "Microsoft Windows Server 2003 Standard x64 Edition"
        os_number = self.updates.get_os_number(os_informations_2003)
        self.assertIsNone(os_number)

        # R2 is still supported
        os_informations_2003["os"] = "Windows Server 2003 R2 Enterprise"
        os_informations_2003["arch"] = "x64"
        os_number = self.updates.get_os_number(os_informations_2003)
        self.assertEqual(os_number, 10559)

        os_informations_2003["arch"] = "x86"
        os_number = self.updates.get_os_number(os_informations_2003)
        self.assertEqual(os_number, 10558)

        # 6.1.7601 Service Pack 1 Build 7601, x64-based PC, Microsoft Windows Server 2008 R2 Enterprise
        os_informations_2008 = dict()
        os_informations_2008["version"] = "6.1.7601 Service Pack 1 Build 7601"
        os_informations_2008["arch"] = "x64"
        os_informations_2008["os"] = "Microsoft Windows Server 2008 R2 Enterprise"
        os_number = self.updates.get_os_number(os_informations_2008)
        self.assertEqual(os_number, 10051)

        os_informations_2012 = dict()
        os_informations_2012["version"] = "6.3.9600 N/A version 9600"
        os_informations_2012["arch"] = "x64"
        os_informations_2012["os"] = "Microsoft Windows Server 2012 R2 Standard"
        os_number = self.updates.get_os_number(os_informations_2012)
        self.assertEqual(os_number, 10483)

    # Windows test archives are not available anymore
    #def test_updates(self):
    def old_updates(self):
        self.logger.info("Testing Windows updates...")

        os_informations_dict = dict()
        os_informations_dict["version"] = "6.3.9600 N/A version 9600"
        os_informations_dict["arch"] = "x64"
        os_informations_dict["os"] = "Microsoft Windows Server 2012 R2 Standard"

        update_list = "pycaf2/test/resources/windows/installed_patches_server_2008.txt"
        if not os.path.exists(update_list):
            raise Exception("File: {} does not exist.".format(update_list))

        with open(update_list, 'r', encoding='utf-8', errors='ignore') as f:
            updates_file_content = f.read()

        if updates_file_content is None:
            self.logger.error("File content {} is none.".format(update_list))
            return

        self.updates.check_config(updates_file_content, os_informations_dict)

        #for i in self.updates.get_infos():
        #    self.logger.info(i)
        #for i in self.updates.get_improvements():
        #    self.logger.info(i)
        #for i in self.updates.get_warnings():
        #    self.logger.warning(i)
        #for i in self.updates.get_criticals():
        #    self.logger.error(i)
