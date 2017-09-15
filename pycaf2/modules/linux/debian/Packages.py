# coding: utf8

import urllib.request
import gzip
import tempfile
import re
import os
import subprocess
from collections import OrderedDict

from pycaf2.lib.module import Module

class Packages(Module):
    def __init__(self):
        super(Packages, self).__init__()
        self.name = "Packages"
        self.distrib_version = None
        self.os_name = None
        self.distribution = None
        self.arch = None

        # Attributes related to sources list
        self.distribution_list = []
        self.url_list = []

        self.uptodate_packages = OrderedDict()
        self.obsolete_packages = OrderedDict()
        self.unknown_packages = OrderedDict()


    def run(self, server):
        """ Module main method
        """

        self.distrib_version = server.os_informations["code_name"]
        if not self.distrib_version:
            raise Exception("Linux version is unknown. Cannot analyze packages list.")

        if self.distrib_version == "unknown":
            self.logger.error("Distribution version is unknown, cannot check for packages list.")
            self.logger.error("Use parameter --version to force the distribution to \"jessie\" for example.")
            return

        self.os_name = server.os_informations["os"]
        if not self.os_name:
            raise Exception("OS name is unknown. Cannot analyze packages list.")
        if "distribution" in server.os_informations:
            if server.os_informations["distribution"] == "ubuntu":
                self.distribution = "ubuntu"

        self.arch = server.os_informations["arch"]
        if not self.arch:
            raise Exception("Arch is unknown. Cannot analyze packages list.")
        # Transform arch to Debian nomenclature : amd64 and i386
        if "x64" == self.arch:
            self.arch = "amd64"
        elif self.arch == "x86":
            self.arch = "i386"

        # Get config file and parse it
        pkg_config_content = server.file_list.get_file_content("pkg_list.txt$")
        if pkg_config_content is None:
            self.logger.error("pkg_list.txt missing.")
            return



        # Get packages sources file and parse it
        # TODO: make this work when we have source files in sources.list.d/
        #sources_list_content = server.file_list.get_files_list("^.*\.list$")
        distrib_sources_content = server.file_list.get_file_content("sources.list$")
        if distrib_sources_content is None:
            raise Exception("File sources.list missing.")

        self.check_config(pkg_config_content, distrib_sources_content)


    def check_config(self, pkg_config_content, distrib_sources_content):
        """ Check the configuration
        """
        self.__parse_sources_list(distrib_sources_content)
        installed_packages = self.parse_server_pkg_list(pkg_config_content)
        if not installed_packages:
            raise Exception("No package has been found on the server, checkout file pkg_list.txt.")

        # Launch analysis
        self.__analyze(installed_packages)
        self.__set_results()


    def __parse_sources_list(self, distrib_sources_content):
        """
        Gets all packages sources defined in distrib_sources_content.
        self.distribution_list is set with content of the file.
        """

        # regex: only take binary packages (no deb-src for ex.)
        source_list_expression = r"^deb(\s)+(\[.*\](\s)+)?(?P<url>[A-Za-z:\/.]+)(\s)(?P<distribution>[A-Za-z-.]+)(\s)([A-Za-z- ]+)$"
        sources_reg = re.compile(source_list_expression)

        lines = distrib_sources_content.split('\n')

        found_main = found_updates = found_backports = False

        for line in lines:
            if sources_reg.match(line) is not None:
                result_re = sources_reg.match(line)
                url = result_re.group('url')
                distribution = result_re.group('distribution')

                self.logger.debug("Found URL {} for {}".format(url, distribution))
                if distribution not in self.distribution_list:
                    self.logger.debug("Found {}".format(distribution))
                    if distribution == self.distrib_version:
                        found_main = True
                        if url not in self.url_list:
                            self.url_list.append(url)
                    elif "{}-updates".format(self.distrib_version) == distribution:
                        found_updates = True
                        if url not in self.url_list:
                            self.url_list.append(url)
                    elif "{}-backports".format(self.distrib_version) == distribution:
                        found_backports = True
                        if url not in self.url_list:
                            self.url_list.append(url)
                    else:
                        self.logger.error("Found line \"{}\" in sources.list. Check it out manually.".format(line))
                else:
                    self.logger.debug("Already found: {}".format(distribution))

            else:
                pass
                #self.logger.debug("Warning, line: {} is not recognized by regex.".format(line))

        if found_main:
            self.distribution_list.append(self.distrib_version)
        if found_updates:
            self.distribution_list.append("{}-updates".format(self.distrib_version))
        if found_backports:
            self.distribution_list.append("{}-backports".format(self.distrib_version))


    def parse_server_pkg_list(self, pkg_config_content):
        """
        Parses pkg_config_content to extract installed packages of the server.
        Returns a dict(): package_name -> version.
        """
        pkg_expression = r"^ii(\s)+(?P<pkg_name>[A-Za-z0-9:\-~.+]+)(\s)+(?P<pkg_version>[A-Za-z0-9:\-~,.+\[\]]+)(\s)+(?P<pkg_arch>[A-Za-z0-9]+)(\s)+(?P<pkg_desc>.*)$"
        pkg_reg = re.compile(pkg_expression)

        lines = pkg_config_content.split('\n')
        installed_packages = OrderedDict()
        for line in lines:
            if pkg_reg.match(line) is not None:
                result_re = pkg_reg.match(line)
                pkg_name = result_re.group('pkg_name')
                # Check that package_name does not end with :amd64
                if pkg_name[-6:] == ":amd64":
                    pkg_name = pkg_name[:-6]
                pkg_version = result_re.group('pkg_version')
                installed_packages[pkg_name] = pkg_version
            else:
                pass #self.logger.debug("Warning, line: {} is not recognized by regex.".format(line))

        return installed_packages
        #self.logger.debug("Installed packages are: {}".format(installed_packages))


    def __download_packages_from_site(self, distribution):
        """
        Downloads up to date packages of distribution on the distrib website.
        Returns a string containing all packages with their version up to date.
        """
        # distrib packages are available at this site :
        # https://packages.distrib.org/fr/X/allpackages?format=txt.gz
        url = None
        if "debian" in self.os_name :
            url = "https://packages.debian.org/{}/allpackages?format=txt.gz".format(distribution)
        if self.distribution is not None:
            if self.distribution == "ubuntu":
                url = "https://packages.ubuntu.com/{}/allpackages?format=txt.gz".format(distribution)
        if url is None:
            self.logger.error("Did not found if distribution is Ubuntu or Debian, quitting.")
            return

        self.logger.debug("Getting URL: {}".format(url))
        try:
            connection = urllib.request.urlopen(url)
            content = connection.read()
            connection.close()
        except Exception as e:
            self.logger.error("Failed to download packages from: {}.".format(url))
            return


        # Cannot decode GZip directly, so go through a tempfile
        try:
            _, temp_path = tempfile.mkstemp()
            self.logger.debug("Downloading temporary files in {}".format(temp_path))
            with open(temp_path, "wb") as f:
                f.write(content)
            with gzip.open(temp_path, 'rt') as f:
                download_packages = f.read()
        except Exception as e:
            self.logger.error("Gunzip has failed with error: {}".format(e))
            self.logger.error("URL {} may not be a valid URL for packages versions, check it out.".format(url))
            return
        #self.logger.debug("Downloaded packages: {}".format(download_packages))

        # Remove temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return download_packages


    def __compare_versions(self, distrib, dict1, dict2, temporary_obsoletes):
        """
        Compares dict1 with dict2 in function of the repo:
        * stable: if equal => package is uptodate ; if inferior => consider package as temporary
        obsoletes, but it will be check in updates ; if superior => package has to be checked in updates and backports.
        * stable-updates: if equal => package is uptodate ; if inferior => package is
        obsolete ; if superior => package is unknown.
        * stables-backports: if equal => package is uptodate ; if inferior => package
        is obsolete ; if superior => package is unknown.

        Parameters:
        * distrib: the distribution (stable, stable-updates, stable-backports)
        * dict1 must contain packages from the server,
        * dict_2 must contain packages downloaded from the internet.

        Returns: dicts containing every packages[version] that has not been compared.
        """
        self.logger.debug("Comparing version for distrib: {}".format(distrib))

        uptodate_packages = OrderedDict()
        obsolete_packages = OrderedDict()

        for package, version in dict1.items():
            if not package in dict2:
                continue

            try:
                #self.logger.debug("Version: {}".format(version))
                subprocess.check_output(["dpkg", "--compare-versions", version, "eq", dict2[package]])
                # Package versions are equal
                uptodate_packages[package] = version

            except subprocess.CalledProcessError:
                # Package versions are not equal, check if version is inferior only if we are in updates or backports
                try:
                    subprocess.check_output(["dpkg", "--compare-versions", version, "lt", dict2[package]])
                    # Version of server is less than on the net
                    if ("updates" in distrib) or ("backports" in distrib):
                        obsolete_packages[package] = version
                    else:
                        # Push in temporary dict
                        temporary_obsoletes[package] = version
                except subprocess.CalledProcessError:
                    continue

        # If we are in updates or backports distrib, check for temporary_obsoletes dict
        tmp_list = []
        if ("updates" in distrib) or ("backports" in distrib):
            for package, version in temporary_obsoletes.items():
                #self.logger.debug("Checking temporary: {} in version {}".format(package, version))
                if not package in dict2:
                    obsolete_packages[package] = version
                    tmp_list.append(package)
                else:
                    try:
                        subprocess.check_output(["dpkg", "--compare-versions", version, "eq", dict2[package]])
                        # Package versions are equal
                        uptodate_packages[package] = version
                        tmp_list.append(package)
                    except subprocess.CalledProcessError:
                        # Package versions are not equal, check if version is inferior only if we are in updates or backports
                        try:
                            subprocess.check_output(["dpkg", "--compare-versions", version, "lt", dict2[package]])
                            # Version of server is less than on the net
                            obsolete_packages[package] = version
                            tmp_list.append(package)
                        except subprocess.CalledProcessError:
                            continue
        for i in tmp_list:
            del temporary_obsoletes[i]

        return uptodate_packages, obsolete_packages, temporary_obsoletes


    def __analyze(self, installed_packages):

        # Tell user of packages that will be downloaded and checked
        if not self.distribution_list:
            raise Exception("Distribution list is empty, something went wrong.")
        self.logger.debug("distrib distribution packages that will be check: {}".format(self.distribution_list))

        self.logger.debug("distrib {} packages analysis in progress...".format(self.distrib_version))

        # Regex for extracting usefull data
        #pkg_release_expression = r"^(?P<pkg_name>[A-Za-z0-9:\.\-~+]+)(\s)+\((?P<pkg_version>[0-9a-zA-Z\.\-\+:~]+).*\)(\s)+(?P<pkg_desc>.*)$"
        pkg_release_expression = r"^(?P<pkg_name>[A-Za-z0-9:\.\-~+]+)(\s)+\((?P<pkg_version>.[^)]*)\)(\s)+(?P<pkg_desc>.*)$"
        pkg_release_reg = re.compile(pkg_release_expression)

        # Regex for extracting architecture dependant package versions
        # ex: (0.8.0.3-7+b1 [amd64, arm64, i386, mipsel, s390x], 0.8.0.3-7 [mips])
        version_expression = r"(?P<version>(.*))(\s)+\[.*"
        version_expression_reg = re.compile(version_expression)

        temporary_obsoletes = OrderedDict()
        # Check package loop:
        # For each distribution in distribution_list [distrib, distrib_updates, distrib_backports].
        # Download up to date version from distrib website
        # Build corresponding dict() package -> version
        # Compare built dict() with the dict containing packages installed on the system.
        # Send to compare function
        for distrib in self.distribution_list:
            up_to_date_packages_content = self.__download_packages_from_site(distrib)
            if up_to_date_packages_content is None:
                continue
            up_to_date_packages_list = up_to_date_packages_content.split('\n')
            # Dictionnary of release packages
            up_to_date_packages = OrderedDict()

            for package in up_to_date_packages_list:
                #self.logger.debug("package : {}".format(package))
                if pkg_release_reg.match(package) is not None:
                    result_re = pkg_release_reg.match(package)
                    pkg_name = result_re.group('pkg_name')
                    pkg_version = result_re.group('pkg_version')

                    # Some package versions are dependant of the architecture
                    if ('[' in pkg_version) and (']' in pkg_version):
                        #self.logger.debug("package : {}".format(package))
                        res = pkg_version.split('],')
                        for i in res:
                            #self.logger.debug("split: {}".format(i))
                            if self.arch in i:
                                #self.logger.debug("arch: {}".format(i))
                                if version_expression_reg.match(i) is not None:
                                    result_re = version_expression_reg.match(i)
                                    version = result_re.group('version')
                                    #self.logger.debug("Replacing version: {} with: {}".format(pkg_version, version))
                                    pkg_version = version

                    up_to_date_packages[pkg_name] = pkg_version

                else:
                    continue #if not "virtual" in package: # Most of mismatch is because of virtual packages
                        #self.logger.error("Warning, line: {} is not recognized by regex.".format(package))

            #self.logger.info("Downloaded packages: {}".format(release_dict))

            ## Compare !
            _uptodate_packages, _obsolete_packages, temporary_obsoletes = self.__compare_versions(
                            distrib, installed_packages, up_to_date_packages, temporary_obsoletes)

            ## Update results
            ## And remove package from installed package since we have taken a decision (uptodate/obsolete)
            if _uptodate_packages:
                self.logger.debug("Found {} packages up to date on {}".format(len(_uptodate_packages), distrib))
                self.uptodate_packages.update(_uptodate_packages)
                for pack in _uptodate_packages.keys():
                    del installed_packages[pack]
            if _obsolete_packages:
                self.logger.debug("Found {} obsoletes packages".format(len(_obsolete_packages)))
                self.obsolete_packages.update(_obsolete_packages)
                for pack in _obsolete_packages.keys():
                    del installed_packages[pack]


        # end of loop
        if installed_packages:
            # All packages that are still in the list are unknown
            self.unknown_packages.update(installed_packages)



    def __set_results(self):
        """
        Sets all results found by analysis.

        self.url_list = []
        self.uptodate_packages = []
        self.obsolete_packages = []
        self.unknown_packages = []
        """
        self.infos.append("URLs define in sources.list are: {}".format(self.url_list))
        self.infos.append("Number of up to date packages: {}".format(len(self.uptodate_packages)))
        self.warnings.append("Packages unknown({}): {}".format(len(self.unknown_packages), self.unknown_packages))
        self.criticals.append("Packages obsoletes({}): {}".format(len(self.obsolete_packages), self.obsolete_packages))
