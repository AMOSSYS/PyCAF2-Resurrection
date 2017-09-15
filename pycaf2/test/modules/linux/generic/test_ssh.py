#!/usr/bin/python3
# -*- coding: utf8 -*-

import unittest
import os

from pycaf2.lib import Logger
from pycaf2.modules.linux.generic import SSH

class TestSSH (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)

    def test_SSH(self):
        self.logger.info("Testing SSH...")
        ssh_config = "pycaf2/test/resources/linux/sshd_config"
        if not os.path.exists(ssh_config):
            raise Exception("File: {} does not exist.".format(ssh_config))

        with open(ssh_config, 'rt') as f:
            sshd_content = f.read()

        ssh = SSH.SSH()
        ssh.check_config(sshd_content)

        res = ssh.to_string()
        #self.logger.warning("res" + res)
        self.assertEqual(res, """
## General informations:
Permit root login: no
Privilege separation: yes
Permit empty password: no
Protocol: 2
Log level : INFO
RSA authentication: yes
Pubkey authentication: yes

## Improvements:
Port: 22 [DEFAULT]. It is recommended to change the default port.

## Warnings:
X11 Forwarding: yes
Use PAM: yes

## Critical warnings:
""")
        for i in ssh.get_infos():
            self.logger.info(i)
        for i in ssh.get_improvements():
            self.logger.info(i)
        for i in ssh.get_warnings():
            self.logger.warning(i)
        for i in ssh.get_criticals():
            self.logger.error(i)
