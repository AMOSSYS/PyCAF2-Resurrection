#!/usr/bin/python
# -*- coding: utf8 -*-

import unittest
import os

from pycaf2.lib import Logger
from pycaf2.lib.extract import Extract, ExtractionFail
from pycaf2.lib.system import System

class TestSystemMethods (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)
        self.system = System()

    def tearDown(self):
        pass

    # Windows test archives are not available anymore
    #def test_windows_system_info(self):
    def old_windows_system_info(self):
        """
        Returned structure data should be:
        "data": {
            "system_type": "windows",
            "os_name": "Microsoft Windows Server 2012 R2 Standard | Microsoft Windows Server 2008 R2 Enterprise | ...",
            "version": "6.1.7601 Service Pack 1 Build 7601",
            "arch": "x64"
        }

        """
        self.logger.info("Testing Windows OS identification...")

        system_info_server_2003_en = "pycaf2/test/resources/windows/system-info-server-2003-en.txt"
        system_info_server_2008_en = "pycaf2/test/resources/windows/system-info-server-2008-en.txt"
        system_info_server_2012_fr = "pycaf2/test/resources/windows/system-info-server-2012-fr.txt"

        # Server 2003
        with open(system_info_server_2003_en, encoding='utf-8', errors='ignore') as f:
            system_info_server_2003_en_content = f.read()
        if system_info_server_2003_en_content is None:
            raise Exception("Cannot read file {}".format(system_info_server_2003_en))

        score = {"total": 2, "current": 1}
        score, os_name, version, arch = self.system.parse_windows_system_info(
                                system_info_server_2003_en_content, score)

        score = int((score["current"]*100)/score["total"])
        #self.logger.debug("Windows Server 2003\nScore: {}\nOS name: {}\nVersion: {}\nArch: {}".format(
        #                    score, os_name, version, arch))

        self.assertEqual(score, 100)
        self.assertEqual(os_name, "Microsoft Windows Server 2003 Standard x64 Edition")
        self.assertEqual(version, "5.2.3790 Service Pack 2 Build 3790")
        self.assertEqual(arch, "x64")

        # Server 2008
        with open(system_info_server_2008_en, encoding='utf-8', errors='ignore') as f:
            system_info_server_2008_en_content = f.read()
        if system_info_server_2008_en_content is None:
            raise Exception("Cannot read file {}".format(system_info_server_2008_en))

        score = {"total": 2, "current": 1}
        score, os_name, version, arch = self.system.parse_windows_system_info(
                                system_info_server_2008_en_content, score)

        score = int((score["current"]*100)/score["total"])
        #self.logger.debug("Windows Server 2008\nScore: {}\nOS name: {}\nVersion: {}\nArch: {}".format(
        #                    score, os_name, version, arch))
        self.assertEqual(score, 100)
        self.assertEqual(os_name, "Microsoft Windows Server 2008 R2 Enterprise")
        self.assertEqual(version, "6.1.7601 Service Pack 1 Build 7601")
        self.assertEqual(arch, "x64")

        # Server 2012 fr
        with open(system_info_server_2012_fr, encoding='utf-8', errors='ignore') as f:
            system_info_server_2012_fr_content = f.read()
        if system_info_server_2012_fr_content is None:
            raise Exception("Cannot read file {}".format(system_info_server_2012_fr))

        score = {"total": 2, "current": 1}
        score, os_name, version, arch = self.system.parse_windows_system_info(
                                system_info_server_2012_fr_content, score)

        score = int((score["current"]*100)/score["total"])
        #self.logger.debug("Windows Server 2012\nScore: {}\nOS name: {}\nVersion: {}\nArch: {}".format(
        #                    score, os_name, version, arch))
        self.assertEqual(score, 100)
        self.assertEqual(os_name, "Microsoft Windows Server 2012 R2 Standard")
        self.assertEqual(version, "6.3.9600 N/A version 9600")
        self.assertEqual(arch, "x64")



    def test_os_identifier(self):
        self.logger.info("Testing Debian system recognition...")

        extractor = Extract()
        try:
            server = extractor.load_file(os.path.join("pycaf2", "test", "resources", "linux", "PC-77"), False)
        except ExtractionFail:
            raise Exception("Extraction Failed.")

        try:
            os_informations = self.system.os_identifier(server)
            self.logger.info("OS informations: {}".format(os_informations))
        except Exception as e: #OsIdentifierException:
            self.logger.error("Error : %s " % e)
            raise Exception("OS cannot be identified. Use the -o argument to force one.")

        self.assertEqual("linux", os_informations["system_type"])
        self.assertEqual("3.16.0-4-amd64", os_informations["kernel"])
        self.assertEqual("jessie", os_informations["code_name"])
        self.assertEqual("debian", os_informations["os"])
        self.assertEqual("x64", os_informations["arch"])

        # Windows extracted archives are no longer available
        #self.logger.info("Testing Windows system recognition...")
        #extractor = Extract()
        #try:
        #    server = extractor.load_file(os.path.join("pycaf2", "test", "resources", "windows", "export-windows-server-2008"), False)
        #except ExtractionFail:
        #    raise Exception("Extraction Failed.")

        #try:
        #    os_informations = self.system.os_identifier(server)
        #    self.logger.info("OS informations: {}".format(os_informations))
        #except Exception as e: #OsIdentifierException:
        #    self.logger.error("Error : %s " % e)
        #    raise Exception("OS cannot be identified. Use the -o argument to force one.")

        #self.assertEqual("windows", os_informations["system_type"])
        #self.assertEqual("6.1.7601 Service Pack 1 Build 7601", os_informations["version"])
        #self.assertEqual("Microsoft Windows Server 2008 R2 Enterprise", os_informations["os"])
        #self.assertEqual("x64", os_informations["arch"])

    # TODO: test_system_centos
