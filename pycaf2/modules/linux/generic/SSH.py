# coding: utf8

import re

from pycaf2.lib.module import Module

class SSH(Module):

    def __init__(self):
        super(SSH, self).__init__()
        self.name = "SSHD configuration"

    def run(self, server):
        """ Module main method
        """

        files = server.file_list

        # Get update file
        sshd_config_content = files.get_file_content("sshd_config$")
        if sshd_config_content is None:
            self.logger.error("sshd_config missing.")
            return
        self.check_config(sshd_config_content)

        # We can log results here or in parent if necessary
        # this.logger.info(self.oks)
        # this.logger.warning(self.warnings)


    def check_config(self, sshd_config_content):
        """ Check the configuration
        """

        # Regex for extracting usefull data
        ssh_conf = sshd_config_content.split("\n")
        re_port = re.compile("(?P<label>^Port\s+)(?P<port>[0-9]+)")
        re_protocol = re.compile("(?P<label>^Protocol\s+)(?P<protocol>[0-9]+)")
        re_privilege_separation = re.compile("(?P<label>^UsePrivilegeSeparation\s+)(?P<priv_sep>[a-z]+)")
        re_loglevel = re.compile("(?P<label>^LogLevel\s+)(?P<log_level>[A-Z0-9]+)")
        re_permit_root_login = re.compile("(?P<label>^PermitRootLogin\s+)(?P<root_login>[a-z]+)")
        re_rsa_auth = re.compile("(?P<label>^RSAAuthentication\s+)(?P<rsa_auth>[a-z]+)")
        re_pubkey_auth = re.compile("(?P<label>^PubkeyAuthentication\s+)(?P<pubkey_auth>[a-z]+)")
        re_permit_empty_psswd = re.compile("(?P<label>^PermitEmptyPasswords\s+)(?P<perm_empty_psswd>[a-z]+)")
        re_psswd_auth = re.compile("(?P<label>^PasswordAuthentication\s+)(?P<psswd_auth>[a-z]+)")
        re_x11_forward = re.compile("(?P<label>^X11Forwarding\s+)(?P<x11_forward>[a-z]+)")
        re_use_pam = re.compile("(?P<label>^UsePAM\s+)(?P<use_pam>[a-z]+)")

        permit_root_login = []
        password_auth = []
        privilege_separation = []
        x11_forward = []
        port = []
        permit_empty_psswd = []
        protocol = []
        log_level = []
        rsa_auth = []

        pubkey_auth = []
        use_pam = []


        # Check configuration
        for line in ssh_conf:
            if port == []:
                port = re_port.findall(line)
            if pubkey_auth == []:
                pubkey_auth = re_pubkey_auth.findall(line)
            if use_pam == []:
                use_pam = re_use_pam.findall(line)
            if rsa_auth == []:
                rsa_auth = re_rsa_auth.findall(line)
            if log_level == []:
                log_level = re_loglevel.findall(line)
            if protocol == []:
                protocol = re_protocol.findall(line)
            if permit_root_login == []:
                permit_root_login = re_permit_root_login.findall(line)
            if x11_forward == []:
                x11_forward = re_x11_forward.findall(line)
            if password_auth== []:
                password_auth = re_psswd_auth.findall(line)
            if privilege_separation== []:
                privilege_separation = re_privilege_separation.findall(line)
            if permit_empty_psswd== []:
                permit_empty_psswd = re_permit_empty_psswd.findall(line)

        # Check and log results
        if permit_root_login != []:
            if permit_root_login[0][1] == "yes":
                #self.logger.warning("Permit root login: yes [WARNING]")
                self.warnings.append("Permit root login: yes")
            else:
                #self.logger.info("Permit root login: no [OK]")
                self.infos.append("Permit root login: no")

        if port != []:
            if port[0][1] == "22":
                #self.logger.info("Port : %s [DEFAULT]" % port[0][1])
                self.improvements.append("Port: %s [DEFAULT]. It is recommended to change the default port." % port[0][1])
            else:
                #self.logger.info("Port : %s" % port[0][1])
                self.infos.append("Port : %s" % port[0][1])
        if x11_forward != []:
            if x11_forward[0][1] == "yes":
                #self.logger.warning("X11 Forwarding : yes [WARNING]")
                self.warnings.append("X11 Forwarding: yes")
            else:
                #self.logger.info("X11 Forwarding : no [OK]")
                self.infos.append("X11 Forwarding: no")

        if password_auth != []:
            if password_auth[0][1] == "yes":
                #self.logger.warning("Password authentication : yes [WARNING]")
                self.warnings.append("Password authentication: yes")
            else:
                #self.logger.info("Password authentication : no [OK]")
                self.infos.append("Password authentication: no")

        if privilege_separation != []:
            if privilege_separation[0][1] == "yes":
                #self.logger.info("Privilege separation : yes [OK]")
                self.infos.append("Privilege separation: yes")
            else:
                #self.logger.warning("Privilege separation : no [WARNING]")
                self.warnings.append("Privilege separation: no")

        if permit_empty_psswd != []:
            if permit_empty_psswd[0][1] == "yes":
                #self.logger.warning("Permit empty password : yes [WARNING]")
                self.criticals.append("Permit empty password: yes")
            else:
                #self.logger.info("Permit empty password : no [OK]")
                self.infos.append("Permit empty password: no")

        if protocol != []:
            if protocol[0][1] == "2":
                #self.logger.info("Protocol : 2 [OK]")
                self.infos.append("Protocol: 2")
            else:
                #self.logger.warning("Protocol : %d [WARNING]" % int(protocol[0][1]))
                self.criticals.append("Protocol: %d" % int(protocol[0][1]))

        if log_level != []:
            if log_level[0][1] == "INFO":
                #self.logger.info("Log level : INFO [OK]")
                self.infos.append("Log level : INFO")
            else:
                #self.logger.warning("Log level : %s [WARNING]" % int(log_level[0][1]))
                self.warnings.append("Log level: %s" % int(log_level[0][1]))

        if rsa_auth != []:
            if rsa_auth[0][1] == "yes":
                #self.logger.info("RSA authentication : yes [OK]")
                self.infos.append("RSA authentication: yes")
            else:
                #self.logger.warning("RSA authentication : no [WARNING]")
                self.warnings.append("RSA authentication: no")

        if pubkey_auth != []:
            if pubkey_auth[0][1] == "yes":
                #self.logger.info("Pubkey authentication : yes [OK]")
                self.infos.append("Pubkey authentication: yes")
            else:
                #self.logger.warning("Pubkey authentication : no [WARNING]")
                self.warnings.append("Pubkey authentication: no")

        if use_pam != []:
            if use_pam[0][1] == "yes":
                #self.logger.warning("Use PAM : yes [WARNING]")
                self.warnings.append("Use PAM: yes")
            else:
                #self.logger.info("Use PAM : no [OK]")
                self.infos.append("Use PAM: no")
