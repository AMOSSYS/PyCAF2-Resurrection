#!/usr/bin/python3
# -*- coding: utf8 -*-

import unittest
import os

from pycaf2.lib import Logger
from pycaf2.modules.linux.generic import Accounts

class TestAccounts (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)

    def test_Accounts(self):
        self.logger.info("Testing Accounts...")
        passwd = "pycaf2/test/resources/linux/PC-77/passwd.txt"
        if not os.path.exists(passwd):
            raise Exception("File: {} does not exist.".format(passwd))

        with open(passwd, 'rt') as f:
            passwd_content = f.read()
        ok_passwd = True

        shadow = "pycaf2/test/resources/linux/PC-77/etc/shadow"
        if not os.path.exists(shadow):
            raise Exception("File: {} does not exist.".format(shadow))

        with open(shadow, 'rt') as f:
            shadow_content = f.read()
        ok_shadow = True

        accounts = Accounts.Accounts()
        accounts.check_config(passwd_content, shadow_content, ok_passwd, ok_shadow)

        accounts.print_res()
