# coding: utf8

import re
from collections import OrderedDict

from pycaf2.lib.module import Module

class Sudoers(Module):
    def __init__(self):
        super(Sudoers, self).__init__()
        self.name = "Check Sudoers"

        self.aliases = OrderedDict()
        self.defaults_options = []
        self.rules = OrderedDict()

    def run(self, server):
        """ Module main method
        """
        self.files = server.file_list

        # Get update file (/etc/sudoers is prevalent over others)
        sudoers_content = self.files.get_file_content("sudoers$")

        if sudoers_content is None:
            self.logger.error("sudoers missing.")
            return
        self.check_config(sudoers_content)

    def check_config(self, file_content):
        """
        Checkout for additionnal configuration files and concat them into file_content.
        Then parses file_content to identify defined aliases, defined Defaults.
        Finally, parses rules.
        """
        # Checkout additionnal configuration files
        file_content = self.__checkout_additionnal_conf(file_content)

        reg_aliases_exp = r"(?P<alias_type>.*_Alias)\s+((?P<tmp>((?P<alias_name>.*)=(?P<values>.*))))"
        reg_rules_exp = r"(?P<user>[^\s]+)\s+(?P<rule>.+)"

        reg_aliases = re.compile(reg_aliases_exp)
        reg_rules = re.compile(reg_rules_exp)

        for line in file_content.split("\n"):
            line = line.strip()
            _continue = True

            if line and not line.startswith("#"):
                #self.logger.debug("Line: {}".format(line))
                _continue = self.__check_aliases(reg_aliases, line)
                if _continue:
                    _continue = self.__check_defaults(line)
                if _continue: # do not try to parse rule if
                    self.__parse_rules(reg_rules, line)

        self.__set_results()

    def __checkout_additionnal_conf(self, file_content):
        """
        Checkout if we find additionnal configuration files included.
        """

        for line in file_content.split("\n"):
            line = line.strip()

            # Check if we have file inclusion
            if "#includedir" in line[:11]:
                self.logger.debug("Found #includedir line: {}".format(line))
                folder = line.replace("#includedir", "").strip().replace("\"", "")
                if not folder:
                    self.logger.warning("Line is weird, checkout manually: {}".format(line))
                    continue

                tmp_list = self.files.get_files_list("{}/*".format(folder))
                if not tmp_list:
                    self.logger.warning("Cannot retrieve any files in folder {}, checkout manually"
                    .format(folder))
                    continue
                for conf_file in tmp_list:
                    self.logger.debug("Found {} in folder {}".format(conf_file, folder))
                    tmp = self.files.get_file_content(conf_file)
                    if tmp:
                        file_content += tmp
                    else:
                        self.logger.warning("File: {} does not seem to exist, checkout manually".format(conf_file))

            elif "#include" in line[:8]:
                self.logger.debug("Found #include line: {}".format(line))
                conf_file = line.replace("#include", "").strip().replace("\"", "")
                if not folder:
                    self.logger.warning("Line is weird, checkout manually: {}".format(line))
                    continue

                tmp = self.files.get_file_content(conf_file)
                if tmp:
                    #self.logger.debug("Concatenate file: {} to sudoers content".format(tmp))
                    file_content += tmp
                else:
                    self.logger.warning("File: {} does not seem to exist, checkout manually".format(conf_file))

        return file_content


    def __check_aliases(self, reg_aliases, line):
        """
        Parses aliases content
        """
        _continue = True
        match_alias = reg_aliases.match(line)
        if match_alias is not None:
            #self.logger.debug("Found Alias line: {}".format(line))
            _continue = False
            alias_type = match_alias.group("alias_type").strip()
            if alias_type not in ["User_Alias", "Runas_Alias", "Host_Alias", "Cmnd_Alias"]:
                self.logger.error("Found an unknown alias type in line: {}"
                .format(line))
                return _continue

            if alias_type in self.aliases:
                self.logger.warning("Alias type {} already exist, sudoers file is not correct".format(alias_type))
                return _continue


            name_values_dict = OrderedDict()
            alias_name = match_alias.group("alias_name").strip()
            if ":" in alias_name: #BUG: this may not work if the list is composed of a non-unix group (which contains ":")
                # Alias name was not correctly parsed because of
                # the possibility to have several names of one type
                tmp = match_alias.group("tmp")
                for pair_name_values in tmp.split(":"):
                    alias_name = pair_name_values.split("=")[0].strip()
                    values = pair_name_values.split("=")[1].strip()
                    values_array = values.split(",")
                    name_values_dict[alias_name] = values_array

                    self.logger.debug("Found alias type: {} with name: {} and values: {}"
                    .format(alias_type, alias_name, values))

            else:
                values = match_alias.group("values").strip()
                values_array = values.split(",")
                name_values_dict[alias_name] = values_array

                self.logger.debug("Found alias type: {} with name: {} and values: {}"
                .format(alias_type, alias_name, values))

            self.aliases[alias_type] = name_values_dict

        return _continue

    def __check_defaults(self, line):
        """
        Checks the Defaults options.
        For example, the default "secure_path" has to be checked so there is no
        unknown folders. If an unknown folder is used, the auditor should check its permissions.
        """
        _continue = True
        line_lower = line.lower()
        # Replace all tabulations with space
        line_lower.replace("\t", " ")

        if "defaults" in line_lower:
            #self.logger.debug("Found Defaults line: {}".format(line))
            _continue = False
            default_param = line.lower().replace("defaults", "").strip()
            self.defaults_options.append(default_param)

            if default_param[0] in [":", "@", ">", "!"]:
                self.warnings.append("Defaults parameter is specific to a host, user, cmnd or runas. Checkout manually: {}"
                .format(line))

            # If we have the secure_path default, checkout it does not have any unknown value
            if "secure_path" in default_param:
                log = True
                self.logger.debug("Found Defaults secure_path entry, checking folders...")
                secure_path = default_param.replace("secure_path=", "").replace("\"", "")
                for folder in secure_path.split(":"):
                    if folder not in ["/usr/local/sbin", "/usr/local/bin", "/usr/sbin"
                    ,"/usr/bin", "/sbin", "/bin"]:
                        self.criticals.append("Secure_path is unknown, checkout manually: {}"
                        .format(folder))
                        log = False
                if log:
                    self.logger.debug("Secure_path entries all good.")

            elif "env_editor" in default_param:
                self.logger.debug("Found Defaults env_editor entry")
                env_editor = default_param.replace("env_editor=", "").replace("\"", "")
                self.criticals.append("Env editor is set to: {}. This may create a security"
                " hole as it allows the user to run any arbitrary command as root without logging."
                " See https://www.sudo.ws/man/sudoers.man.html for additionnal information."
                .format(env_editor))

            elif "fast_glob" in default_param:
                self.logger.debug("Found Defaults fast_glob entry")
                self.criticals.append("Fast_glob may have security implications. Checkout "
                "https://www.sudo.ws/man/sudoers.man.html")

            elif "!authenticate" in default_param:
                self.criticals.append("The option authenticate is disabled for someone, checkout manually: {}"
                .format(default_param))
        return _continue

    def __parse_rules(self, reg_rule, line):
        """
        Parses rules to build attributes self.rules.
        """
        #self.logger.debug("Parsing line: {}".format(line))

        rule_alias = reg_rule.match(line)
        if rule_alias is not None:
            user = rule_alias.group("user")
            rule = rule_alias.group("rule")

            if user not in self.rules:
                self.rules[user] = []
            self.rules[user].append(rule)

    def __set_results(self):
        """
        Sets all results found by analysis.
        """
        if self.aliases:
            self.infos.append("Defined aliases are: {}".format(self.aliases))
        if self.defaults_options:
            self.infos.append("Defaults: {}".format(self.defaults_options))
        if self.rules:
            self.infos.append("Rules: {}".format(self.rules))
