# -*- coding: utf8 -*-

import re
import traceback

from pycaf2.lib import Logger

class System(object):
    def __init__(self):
        self.logger = Logger.getLogger(__name__)

        # Don't forget to update those lists
        self.debian_versions = {
            "4.0": "etch",
            "5.0": "lenny",
            "6.0": "squeeze",
            "7": "wheezy",
            "8": "jessie",
            "9": "stretch",
        }
        self.ubuntu_versions = {
            "8.04": "hardy heron",
            "8.10": "intrepid ibex",
            "9.04": "jaunty jackalope",
            "9.10": "karmic koala",
            "10.04": "lucid lynx",
            "10.10": "maverick meerkat",
            "11.04": "natty narwhal",
            "11.10": "oneiric ocelot",
            "12.04": "precise pangolin",
            "12.10": "quantal quetzal",
            "13.04": "raring ringtail",
            "13.10": "saucy salamender",
            "14.10": "utopic unicord",
            "15.04": "vivic vervet",
            "15.10": "wily werewolf",
            "16.10": "yakkety yak"
        }

    def os_identifier(self, server):
        """ Tries to detect os.
        For the moment, you have to append your new calculate_score method for any new system.
        @TODO: load thees automatically.

        Structure has the following format:
        * for Linux
            {"score": score,
                "data": {
                    "system_type": "linux",
                    "os": "debian|redhat|slackware|suse|gentoo|archlinux|generic", (the main Linux distributions)
                    "kernel": kernel,
                    "distribution": "debian|ubuntu|opensuse|fedora",
                    "codename": "jessie|stretch|xenial",
                    "arch": "x86|x64"
                }
            }
        * for Windows:
                "data": {
                    "system_type": "windows",
                    "os": "Microsoft Windows Server 2012 R2 Standard | Microsoft Windows Server 2008 R2 Enterprise | ...",
                    "version": "6.1.7601 Service Pack 1 Build 7601",
                    "arch": "x86|x64"
                }
        """
        self.logger.debug("Trying to identify OS...")
        self.server = server

        os_scores = []
        os_scores.append(self.calculate_score_debian())
        os_scores.append(self.calculate_score_generic_linux())
        os_scores.append(self.calculate_score_centos())
        os_scores.append(self.calculate_score_generic_windows())

        sorted_scores = sorted(os_scores, key=lambda x: x["score"], reverse=True)
        self.logger.info("\n## OS detection :")
        for score in sorted_scores:
            self.logger.info("%s : %d%%" % (score["data"]["os"], score["score"]))

        return sorted_scores[0]["data"]


    def calculate_score_generic_windows(self):
        """
        Calculates score for Windows system
        """
        self.logger.debug("Calculating score for windows")

        score = {"total": 0, "current": 0}
        files = self.server.file_list

        score["total"] += 1
        if files.file_exists("win_version.txt$"):
            score["current"] += 1

        score["total"] += 1

        system_info_content = files.get_file_content("system_info.txt$")
        if system_info_content is not None:
            score, os_name, version, arch = self.parse_windows_system_info(system_info_content, score)
        else:
            os_name = "windows"
            arch = "x86"
            version = "unknown"

        self.logger.debug("Score is: {}".format(int((score["current"]*100)/score["total"])))
        return {"score": int((score["current"]*100)/score["total"]),
                "data": {
                    "system_type": "windows",
                    "os": os_name,
                    "version": version,
                    "arch": arch
                    }
               }

    def parse_windows_system_info(self, system_info_content, score):
        """
        Parses Windows system info.
        Careful with the cast: we cannot make the strings lower case because of
        how Microsoft website deals with cast...
        """
        #self.logger.debug("Content: {}".format(system_info_content))
        version = "Unknown"
        arch = "x86"
        os_name = "Unknown"

        regex_os_name_fr = r"Nom du syst(.?)me d'exploitation:(\s)*(?P<os_name>.+)"
        regex_os_name_en = r"OS Name:(\s)*(?P<os_name>.+)"
        regex_os_version_fr = r"Version du syst(.?)me:(\s)*(?P<os_version>.+)"
        regex_os_version_en = r"OS Version:(\s)*(?P<os_version>.+)"
        regex_os_type_fr = r"Type du syst(.?)me:(\s)*(?P<os_type>.+)"
        regex_os_type_en = r"System Type:(\s)*(?P<os_type>.+)"

        try:
            score["current"] += 1

            #system_info_content = system_info_content.replace("\x00", "")
            #self.logger.info(system_info_content)
            # Check if we are in french, english or else
            first_line = system_info_content.split('\n')[1].lower()
            if "nom" in first_line:
                self.logger.debug("System info seems to be in FR")
                regex_os_name = re.compile(regex_os_name_fr)
                regex_os_version = re.compile(regex_os_version_fr)
                regex_os_type = re.compile(regex_os_type_fr)
            elif "name" in first_line:
                self.logger.debug("System info seems to be in EN")
                regex_os_name = re.compile(regex_os_name_en)
                regex_os_version = re.compile(regex_os_version_en)
                regex_os_type = re.compile(regex_os_type_en)

            else:
                raise Exception("Cannot find any name or nom in system information content: {}"
                                    .format(first_line))

            for line in system_info_content.split('\n'):
                line = line.rstrip() # some lines may have spaces at the end
                if (regex_os_name.match(line) is not None) and (os_name == "Unknown"):
                    result_re = regex_os_name.match(line)
                    os_name = result_re.group('os_name')
                elif (regex_os_version.match(line) is not None) and (version == "Unknown"):
                    result_re = regex_os_version.match(line)
                    version = result_re.group('os_version')
                elif (regex_os_type.match(line) is not None) and (arch == "x86"):
                    result_re = regex_os_type.match(line)
                    arch = result_re.group('os_type')
                    if "x64" in arch:
                        arch = "x64"

            # Windows server 2003 may have things like (R), sigh...
            # ex: "Microsoft(R) Windows(R) Server 2003 Standard x64 Edition"
            if "(R)" in os_name:
                os_name = os_name.replace("(R)", "")

        except Exception:
            tb = traceback.format_exc()
            self.logger.error(tb)

        finally:
            return score, os_name, version, arch


    def calculate_score_centos(self):
        self.logger.debug("Calculating score for CentOS")
        self.logger.debug("Not implemented yet")
        return {"score": 0,
                "data": {
                    "system_type": "linux",
                    "os": "centos",
                    "code_name": "Unknown",
                    "arch": "x86",
                    "kernel": "Unknown"
                    }
               }

    def calculate_score_generic_linux(self):
        self.logger.debug("Calculating score for generic Linux")

        score = {"total": 0, "current": 0}
        files = self.server.file_list

        score["total"] += 1

        if files.file_exists("uname.txt"):
            score["current"] += 1

        score["total"] += 1

        if files.file_exists("/etc/X11"):
            score["current"] += 1

        arch = "x86"
        kernel = "unknown"

        try:
            uname_content = files.get_file_content("uname.txt")
            if uname_content is not None:
                #logging.debug("uname: {}".format(uname_content))
                if "amd64" in uname_content.lower():
                        arch = "x64"
                kernel = uname_content.split(" ")[2]
        except IOError:
            # If file does not exist, continue scoring anyway
            self.logger.debug("File uname.txt exists but is not accessible")

        code_name = "unknown"
        # BUG: If a file point to an absolute path, we may parse a file of our system -_-
        try:
            os_release_content = files.get_file_content("os-release.txt")
            if os_release_content is not None:
                os_release_content = os_release_content.replace("\x00", "").split("\n")
                for infoline in os_release_content:
                    if "VERSION=" in infoline:
                        code_name = infoline.replace("VERSION=", "").replace('"', "")
                        break
        except IOError:
            # If file does not exist, continue scoring anyway
            self.logger.debug("File /etc/os-release exists but is not accessible")

        # Generic Linux always get a -1 malus
        score = int((score["current"]*100)/score["total"])
        if score > 1:
            score -= 1

        self.logger.debug("Score is: {}".format(score))
        return {"score": score,
                "data": {
                    "system_type": "linux",
                    "os": "generic",
                    "kernel": kernel,
                    "code_name": code_name,
                    "arch": arch}
               }


    def calculate_score_debian(self):
        self.logger.debug("Calculating score for debian")

        score = {"total": 0, "current": 0}
        files = self.server.file_list
        #self.logger.debug("Files: {}".format(files))

        score["total"] += 1
        if files.file_exists("debian_version"):
            score["current"] += 1

        score["total"] += 1
        if files.file_exists("uname.txt"):
            score["current"] += 1

        score["total"] += 1
        if files.file_exists("/etc/X11"):
            score["current"] += 1

        arch = "x86"
        kernel = "unknown"
        distrib = "debian"
        try:
            uname_content = files.get_file_content("uname.txt")
            if uname_content is not None:
                if "amd64" in uname_content.lower() or "x86_64" in uname_content.lower():
                    arch = "x64"
                kernel = uname_content.split(" ")[2] # @bug: this may throw exception
                if "ubuntu" in uname_content.lower():
                    distrib = "ubuntu"
        except IOError:
            # If file does not exist, continue scoring anyway
            self.logger.debug("File uname.txt exists but is not accessible")

        code_name = "unknown"
        version_id = None
        try:
            os_release_content = files.get_file_content("os-release")
            if os_release_content is not None:
                os_release_content = os_release_content.replace("\x00", "").split("\n")

                for infoline in os_release_content:
                    infoline = infoline.lower()
                    if "id=" in infoline:
                        tmp = infoline.replace("id=", "").replace("\"", "")
                        if tmp == "ubuntu" and distrib != "ubuntu":
                            distrib = "ubuntu"
                    if "version_id=" in infoline:
                        version_id = infoline.replace("version_id=", "").replace("\"", "")
                    if "version_codename=" in infoline: # this works for Ubuntu only on our tests
                        code_name = infoline.replace("version_codename=", "")
                        break
        except IOError:
            # If file does not exist, continue scoring anyway
            self.logger.debug("File /etc/os-release exists but is not accessible")

        # If code_name was not found, set it relative to the extracted version_id
        if (code_name == "unknown") and (version_id is not None):
            if distrib == "debian":
                if version_id in self.debian_versions:
                    code_name = self.debian_versions[version_id]

            if distrib == "ubuntu":
                if version_id in self.ubuntu_versions:
                    code_name = self.ubuntu_versions[version_id]


        self.logger.debug("Score is: {}".format(int((score["current"]*100)/score["total"])))
        return {"score": int((score["current"]*100)/score["total"]),
                "data": {
                    "system_type": "linux",
                    "os": "debian",
                    "kernel": kernel,
                    "distribution": distrib,
                    "code_name": code_name,
                    "arch": arch
                }
               }
