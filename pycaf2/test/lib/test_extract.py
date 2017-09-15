#!/usr/bin/python
# -*- coding: utf8 -*-

import unittest
import os
import shutil

from pycaf2.lib.extract import Extract
from pycaf2.lib.file_list import FileList
from pycaf2.lib import Logger

class TestExtractMethods (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)

        # When testing, push folders to delete in self.folders
        self.folders = []


    def tearDown(self):
        # Clean up extracted folders
        for folder in self.folders:
            if os.path.exists(folder):
                self.logger.debug("Cleaning directory: {}".format(folder))
                shutil.rmtree(folder)


    def test_debian_archive(self):
        """ Extracting debian archive should complete dump with a "folder" and a "file_list"
        """
        self.logger.info("Testing debian extract...")

        have_to_extract = True
        dump_file = os.path.join("pycaf2", "test", "resources", "linux", "PC-77.config.10216.tar.bz2")
        if not os.path.exists(dump_file):
            raise Exception("Path {} does not exist.".format(dump_file))

        extractor = Extract()
        server = extractor.load_file(dump_file, have_to_extract)
        if server.extracted_folder is not None:
            self.folders.append(server.extracted_folder)

        self.assertIsInstance(server.extracted_folder, str)
        self.assertIsInstance(server.file_list, FileList)

        uname_content = server.file_list.get_file_content("uname.txt$")
        self.assertIn("Linux PC-77 3.16.0-4-amd64", uname_content)


    def test_windows_archive(self):
        self.logger.info("Testing Windows extract...")

        have_to_extract = True
        dump_file = os.path.join("pycaf2", "test", "resources", "windows", "export-windows-server-2008.zip")
        if not os.path.exists(dump_file):
            raise Exception("Path {} does not exist.".format(dump_file))

        extractor = Extract()
        server = extractor.load_file(dump_file, have_to_extract)
        self.folders.append(server.extracted_folder)

        self.assertIsInstance(server.extracted_folder, str)
        self.assertIsInstance(server.file_list, FileList)

        system_info_content = server.file_list.get_file_content("system_info.txt$")
        self.assertIn("Microsoft Windows Server 2008 R2 Enterprise", system_info_content)
