# -*- coding: utf8 -*-

import re
import requests
import json

from pycaf2.lib.module import Module

class Updates(Module):
    def __init__(self):
        super(Updates, self).__init__()
        self.name = "Updates"

        self.technet_url = 'https://technet.microsoft.com/security/bulletin/services/GetBulletins?searchText=%(os_number)d&sortField=0&sortOrder=1&currentPage=1&bulletinsPerPage=10000&locale=en-us'
        self.technet_headers = {"Content-Type":"application/json; charset=utf-8"}

    def run(self, server):
        """ Main method
        """
        #self.logger.getLogger("requests").setLevel(logging.WARNING)
        files = server.file_list

        # Get update file
        updates_file_content = files.get_file_content("installed_patches.txt$")

        if updates_file_content is None:
            self.logger.error("Installed_patches.txt missing.")
            return

        self.check_config(updates_file_content, server.os_informations)


    def check_config(self, updates_file_content, os_informations_dict):
        """
        Firt get the OS number corresponding to extracted versrion from Microsoft web servers.
        Then use this os_number to get available KB and compare them to installed KB.
        """
        # List KB
        kb_file = updates_file_content.replace("\x00", "")
        installed_kb_list = re.findall(r"KB([0-9]+)", kb_file)
        if not installed_kb_list:
            self.logger.warning("Did not import any KB from extracted archive.")
            # We do not exit since this may be legit in very specific cases

        self.logger.info("%d KB imported." % len(installed_kb_list))

        # Get kb from microsoft
        os_number = self.get_os_number(os_informations_dict)

        if os_number is not None:
            microsoft_kb_list = self.get_kb_from_microsoft(os_number)
            installed_kb_details, uninstalled_kb_list = self.get_uninstalled_kb(microsoft_kb_list, installed_kb_list)
            self.infos.append("### Installed KB: ")
            for installed_kb in installed_kb_details:
                self.infos.append("%s - KB%d (%s): %s" % (installed_kb["d"],
                                                     int(installed_kb["KB"]),
                                                     installed_kb["Rating"],
                                                     installed_kb["Title"]))
            self.warnings.append("### Uninstalled KB: ")
            self.criticals.append("### Uninstalled and critical KB: ")
            for uninstalled_kb in uninstalled_kb_list:
                kb_details = "%s - KB%d (%s): %s" % (uninstalled_kb["d"],
                                                        int(uninstalled_kb["KB"]),
                                                        uninstalled_kb["Rating"],
                                                        uninstalled_kb["Title"])

                if "Critical" in kb_details:
                    self.criticals.append(kb_details)
                else:
                    self.warnings.append(kb_details)
        else:
            self.criticals.append("Cannot find any KB for OS: {}. Checkout manually if OS is still maintained by Microsoft."
                    .format(os_informations_dict["os"]))

    def get_uninstalled_kb(self, ms_kb_list, installed_kb_list):
        """ Diff between installed kbs and available kbs
        """
        uninstalled_kb_list = []
        installed_kb_details = []
        for available_kb in ms_kb_list:
            if str(available_kb["KB"]) in installed_kb_list:
                installed_kb_details.append(available_kb)
            else:
                uninstalled_kb_list.append(available_kb)
        return (installed_kb_details, uninstalled_kb_list)

    def get_kb_from_microsoft(self, os_number):
        """ Request kbs list from technet website
        """
        try:
            result = requests.get(self.technet_url % {"os_number": os_number},
                                headers=self.technet_headers, timeout=10)
        except requests.ConnectionError:
            raise Exception("Timeout error: cannot get KB from Microsoft web server.")

        return json.loads(result.text)["b"]


    def get_os_number(self, os_informations):
        """
        Get corresponding os number base on extracted os_informations from https://technet.microsoft.com/fr-fr/security/bulletin.
        """
        version = os_informations["version"]
        arch = os_informations["arch"]
        os_name = os_informations["os"]
        self.logger.debug("{}, {}, {}".format(version, arch, os_name))

        # Construct string for html parsing.. Ugly
        os_name = os_name.replace("Microsoft", "")
        os_name = os_name.replace("Standard", "")
        os_name = os_name.replace("Datacenter", "")
        os_name = os_name.replace("Professionnel", "")
        os_name = os_name.replace("Professionnal", "")
        os_name = os_name.replace("Enterprise", "")
        os_name = os_name.replace("Entreprise", "")
        os_name = os_name.strip()

        #self.logger.debug("OS name has been striped to: {}".format(os_name))
        sp = re.findall("(Service Pack [0-9])", version)
        service_pack_detected = ""
        if len(sp) > 0:
            service_pack_detected = sp[0]
            self.logger.debug("Service Pack has been detected: {}".format(service_pack_detected))

        # This is fucked up Microsoft
        if "x64" in arch:
            if not "2012" in os_name:
                arch = "x64"
            else:
                arch = ""
        elif "Itanium" in arch:
            pass # Keep this arch
        elif "2008" in os_name:
            arch = "32-bit" # For windows server 2008, we have 32-bit in the search name... good job MSF
        else:
            arch = ""

        url = "https://technet.microsoft.com/fr-fr/security/bulletin"
        self.logger.debug("Getting URL: {}".format(url))

        try:
            response = requests.get(url, timeout=10).text
        except requests.ConnectionError:
            self.logger.error("Timeout error: cannot get KB from Microsoft web server.")
            return None

        res = response.split("</option>")
        #self.logger.debug(res)

        # <option value="10530">Active Directory Federation Services 1.x</option>
        regex = r"<option value=\"(?P<id_number>[A-Za-z0-9]+)\">(?P<name>.+)$"
        pkg_reg = re.compile(regex)
        #regex = r"value=\"([0-9]+)\"\>(.+)</option>"
        #versions = re.findall(regex, response)

        for package in res:
            if pkg_reg.match(package) is not None:
                result_re = pkg_reg.match(package)
                id_number = result_re.group('id_number')
                name = result_re.group('name')
                #self.logger.debug("ID number: {}, name: {}".format(id_number, name))
                if os_name in name:
                    # Name has matched: we need to check the arch, and the service pack.
                    self.logger.debug("Matching ID number: {}, name: {}".format(id_number, name))

                    # First discards names when we have no SP and arch
                    if not service_pack_detected:
                        if "Service Pack" in name:
                            continue
                    if not arch:
                        if "x64" in name or "32-bit" in name or "Itanium" in name:
                            continue

                    # Now we can identify our system
                    if arch in name:
                        if service_pack_detected in name:
                            self.logger.debug("Found: id_number: {}, name: {}".format(id_number, name))
                            return int(id_number)


        self.logger.debug("Did not find OS name: {} with arch: {}".format(os_name, arch))
        return None
