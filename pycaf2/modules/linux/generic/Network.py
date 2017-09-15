# coding: utf8

import re
from collections import OrderedDict

from pycaf2.lib.module import Module

class Network(Module):

    class Interface(object):
        """ An interface object.
        """
        def __init__(self):
            self.name = ""
            self.mac = ""
            self.ipv4 = ""
            self.ipv6 = ""
            #self.broadcast = "" not used for now
            self.mask = ""

        def get_details(self):
            res = OrderedDict()
            res["Name"] = self.name
            res["MAC"] = self.mac
            res["IPv4"] = self.ipv4
            res["Mask"] = self.mask
            res["IPv6"] =  self.ipv6
            return res
    # End of Interface object

    def __init__(self):
        super(Network, self).__init__()
        self.name = "Network configuration"

        self.interfaces = []

    def run(self, server):
        """ Module main method
        """

        # Get files
        network_content = server.file_list.get_file_content("network.txt$")

        if network_content is None:
            self.logger.error("network.txt missing.")
            return

        self.check_config(network_content)


    def check_config(self, network_content):
        """ Parses the network configuration and set results
        """

        self.__parse_network_conf(network_content)
        self.__set_results()


    def __parse_network_conf(self, network_content):
        iface_reg_expr_name = r"(?P<name>^[a-zA-Z0-9:\-\"~.+/=]+)"
        iface_reg_expr_mac = r"(?P<var1>.*?(ether|HWaddr).*)(?P<mac>([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})"
        iface_reg_expr_inet4 = r"(?P<var1>.*?inet(?!6).*?)(?P<inet4>([0-9]+.){3}([0-9]+){1})"
        iface_reg_expr_inet6 = r"(?P<var1>.*?inet6:*.*?)(?P<inet6>[0-9a-fA-F:/]+)"
        iface_reg_expr_mask = r"(?P<var1>.*?(m|M)as(k|que).*?)(?P<mask>([0-9]+.){3}([0-9]+){1})"

        reg_iface_name = re.compile(iface_reg_expr_name)
        reg_iface_mac = re.compile(iface_reg_expr_name + iface_reg_expr_mac)
        reg_iface_inet4 = re.compile(iface_reg_expr_inet4)
        reg_iface_inet6 = re.compile(iface_reg_expr_inet6)
        reg_iface_mask = re.compile(iface_reg_expr_mask)

        # Find interfaces
        lines = network_content.split('\n')
        interface = None
        for line in lines:

            # Check if we are in first line of new interface
            match_name = reg_iface_name.match(line)
            match_mac = reg_iface_mac.match(line)
            if match_name is not None:

                if interface is not None: # we have a new interface, append the last one
                    self.interfaces.append(interface)

                # Create new interface
                interface = self.Interface()
                interface.name = match_name.group('name')
                if match_mac is not None:
                    interface.mac = match_mac.group('mac')

                else:
                    if not "lo" in interface.name:
                        self.logger.error("Parses a line where interface is present but not MAC addr: {}".format(line))

                continue

            # check if we are in second line of interface definition
            match_inet4 = reg_iface_inet4.match(line)
            match_mask = reg_iface_mask.match(line)
            if match_inet4 is not None:
                interface.ipv4 = match_inet4.group('inet4')
                if match_mask is not None:
                    interface.mask = match_mask.group('mask')
                else:
                    self.logger.error("Parses a line where inet is present but not mask: {}".format(line))

                continue

            # Check if we are in third line
            match_inet6 = reg_iface_inet6.match(line)
            if match_inet6 is not None:
                interface.ipv6 = match_inet6.group('inet6')
                continue


    def __set_results(self):
        """
        Sets all results found by analysis.
        """
        if self.interfaces:
            self.infos.append("Define interfaces are: {}".format([x.get_details() for x in self.interfaces]))
