#!/usr/bin/python3
# -*- coding: utf8 -*-

import unittest
import os

from pycaf2.lib import Logger
from pycaf2.lib.extract import Extract, ExtractionFail
from pycaf2.modules.linux.generic import Sudoers

class TestSudoers (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)


    def test_sudoers(self):
        """
        Build a server object so we can test for file inclusion.
        """
        self.logger.info("Testing Sudoers included files...")
        extractor = Extract()
        try:
            server = extractor.load_file(os.path.join("pycaf2", "test", "resources", "linux", "PC-77"), False)
        except ExtractionFail:
            raise Exception("Extraction Failed.")

        sudoers = Sudoers.Sudoers()
        sudoers.run(server)

        for i in sudoers.get_infos():
            self.logger.info(i)
        for i in sudoers.get_improvements():
            self.logger.info(i)
        for i in sudoers.get_warnings():
            self.logger.warning(i)
        for i in sudoers.get_criticals():
            self.logger.error(i)

        res = sudoers.to_string()
        #print(res)
        self.maxDiff = None
        self.assertEqual(res, """
## General informations:
Defined aliases are: OrderedDict([('User_Alias', OrderedDict([('OPERATORS', ['joe', ' mike', ' jude']), ('OTHER', ['john'])])), ('Runas_Alias', OrderedDict([('OP', ['root', ' operator'])])), ('Host_Alias', OrderedDict([('OFNET', ['10.1.2.0/255.255.255.0'])])), ('Cmnd_Alias', OrderedDict([('PRINTING', ['/usr/sbin/lpc', ' /usr/bin/lprm'])]))])
Defaults: ['env_reset', 'mail_badpass', 'secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"', ':millert  !authenticate']
Rules: OrderedDict([('root', ['ALL=(ALL:ALL) ALL']), ('%sudo', ['ALL=(ALL:ALL) ALL']), ('user_hid', ['ALL=(ALL) NOPASSWD: ALL']), ('OPERATORS', ['ALL=ALL']), ('linus', ['ALL=(OP) ALL']), ('user2', ['OFNET=(ALL) ALL', 'ALL=(ALL) NOPASSWD: ALL']), ('user3', ['ALL= PRINTING']), ('user4', ['ALL=(ALL) ALL']), ('dgb', ['boulder = (operator) /bin/ls, /bin/kill, /usr/bin/lprm'])])

## Improvements:

## Warnings:
Defaults parameter is specific to a host, user, cmnd or runas. Checkout manually: Defaults:millert  !authenticate

## Critical warnings:
The option authenticate is disabled for someone, checkout manually: :millert  !authenticate
""")
