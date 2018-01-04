#!/usr/bin/python3
# -*- coding: utf8 -*-

import unittest
import os

from pycaf2.lib import Logger
from pycaf2.modules.linux.generic import Network

class TestNetwork (unittest.TestCase):

    def setUp(self):
        self.logger = Logger.getLogger(__name__)

    def test_Network(self):
        self.logger.info("Testing Network...")
        network_config = "pycaf2/test/resources/linux/PC-77/network.txt"
        if not os.path.exists(network_config):
            raise Exception("File: {} does not exist.".format(network_config))

        with open(network_config, 'rt') as f:
            network_config_content = f.read()

        network = Network.Network()
        network.check_config(network_config_content)

        for i in network.get_infos():
            self.logger.info(i)

        res = network.to_string()
        #print(res)
        self.maxDiff = None
        self.assertEqual(res, """
## General informations:
Define interfaces are: [OrderedDict([('Name', 'docker0'), ('MAC', '02:42:9c:ca:9f:35'), ('IPv4', '172.17.0.1'), ('Mask', '255.255.0.0'), ('IPv6', '')]), OrderedDict([('Name', 'eth0'), ('MAC', 'b0:83:fe:78:56:42'), ('IPv4', '192.168.200.198'), ('Mask', '255.255.255.0'), ('IPv6', 'fe80::b283:feff:fe78:5642/64')]), OrderedDict([('Name', 'lo'), ('MAC', ''), ('IPv4', '127.0.0.1'), ('Mask', '255.0.0.0'), ('IPv6', '::1/128')])]

## Improvements:

## Warnings:

## Critical warnings:
""")
