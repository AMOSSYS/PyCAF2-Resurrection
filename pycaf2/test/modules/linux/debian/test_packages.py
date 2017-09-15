#!/usr/bin/python3
# -*- coding: utf8 -*-

import unittest
import os

from pycaf2.lib import Logger
from pycaf2.modules.linux.debian import Packages

class TestPackages (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)

    def test_packages(self):
        self.logger.info("Testing Packages...")
        pkg_config = "pycaf2/test/resources/linux/PC-77/pkg_list.txt"
        sources_list = "pycaf2/test/resources/linux/PC-77/etc/apt/sources.list"
        if not os.path.exists(pkg_config):
            raise Exception("File: {} does not exist.".format(pkg_config))

        with open(pkg_config, 'rt') as f:
            pkg_content = f.read()
        with open(sources_list, 'rt') as f:
            sources_list_content = f.read()

        pkg = Packages.Packages()
        pkg.distrib_version = "jessie"
        pkg.os_name = "debian"
        pkg.arch = "amd64"

        pkg.check_config(pkg_content, sources_list_content)

        #self.logger.info("Up to date packages: {}".format(len(pkg.uptodate_packages)))
        #if pkg.obsolete_packages:
        #    self.logger.error("Packages obsoletes({}): {}".format(len(pkg.obsolete_packages), pkg.obsolete_packages))
        #if pkg.unknown_packages:
        #    self.logger.warning("Packages unknown({}): {}".format(len(pkg.unknown_packages), pkg.unknown_packages))

        for i in pkg.get_infos():
            self.logger.info(i)
        for i in pkg.get_improvements():
            self.logger.info(i)
        for i in pkg.get_warnings():
            self.logger.warning(i)
        for i in pkg.get_criticals():
            self.logger.error(i)

    def test_ubuntu_packages(self):
        self.logger.info("Testing Ubuntu Packages...")
        pkg_config = "pycaf2/test/resources/linux/ubuntu/pkg_list.txt"
        sources_list = "pycaf2/test/resources/linux/ubuntu/sources.list"
        if not os.path.exists(pkg_config):
            raise Exception("File: {} does not exist.".format(pkg_config))

        with open(pkg_config, 'rt') as f:
            pkg_content = f.read()
        with open(sources_list, 'rt') as f:
            sources_list_content = f.read()

        pkg = Packages.Packages()
        pkg.distrib_version = "xenial"
        pkg.os_name = "debian"
        pkg.distribution = "ubuntu"
        pkg.arch = "amd64"

        pkg.check_config(pkg_content, sources_list_content)

        for i in pkg.get_infos():
            self.logger.info(i)
        for i in pkg.get_improvements():
            self.logger.info(i)
        for i in pkg.get_warnings():
            self.logger.warning(i)
        for i in pkg.get_criticals():
            self.logger.error(i)
