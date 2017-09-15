# coding: utf8

from pycaf2.lib.module import Module

class Accounts(Module):

    class User(object):
        """ A user object. Attributes are name, shell, home, UID and GID.
        """
        def __init__(self, user_name, user_shell, user_home, user_uid, user_gid):
            self.name = user_name
            self.shell = user_shell
            self.home = user_home
            self.uid = user_uid
            self.gid = user_gid

        def __repr__(self):
            return "{{'User': '{}', 'shell': '{}', 'home': {}, 'UID': '{}', 'GID': '{}'}}".format(
                            self.name, self.shell, self.home, self.uid, self.gid)

    def __init__(self):
        super(Accounts, self).__init__()
        self.name = "List accounts"

        # @todo: Construct interesting lists of accounts.
        self.users = []

    def run(self, server):
        """ Module main method
        """
        files = server.file_list
        ok_passwd = True
        ok_shadow = True

        # Get files
        passwd_content = files.get_file_content("passwd.txt$")
        shadow_content = files.get_file_content("/etc/shadow$")

        if passwd_content is None:
            self.logger.error("/etc/passwd missing.")
            ok_passwd = False

        if shadow_content is None:
            self.logger.error("/etc/shadow missing.")
            ok_shadow = False

        self.check_config(passwd_content, shadow_content, ok_passwd, ok_shadow)


    def check_config(self, passwd_content, shadow_content, ok_passwd, ok_shadow):
        """ Checks passwd file and shadow file.
        """
        if ok_passwd :
            self.checks_whole_passwd(passwd_content)

            for line in passwd_content.split("\n"):
                line = line.strip()
                if not line.startswith("#"):
                    data = line.split(":")
                    if len(data) > 1:
                        self.checks_line_passwd(data)

        if ok_shadow :
            self.checks_whole_shadow(shadow_content)

            for line in shadow_content.split("\n"):
                line = line.strip()
                if not line.startswith("#"):
                    data = line.split(":")
                    if len(data) > 1:
                        self.checks_line_shadow(data)

        if self.users:
            self.infos.append("Users with shells are: {}".format(self.users))
        else:
            self.infos.append("Did not find any users with shell, that may be weird...")

        #if ok_shadow and ok_passwd:
        #    self.checks_files(files.get_file("passwd.txt$"),files.get_file("/etc/shadow$"))

    #tests on the whole passwd file
    def checks_whole_passwd(self,data):
        self.test_LIN_GEN_ACC_04(data)


    #tests on every line of passwd
    def checks_line_passwd(self, data):
        if len(data) != 7:
            self.logger.warning("Line: {} is not usual, check it out.".format(data))
        else:
            user_name = data[0]
            passwd_in_shadow = data[1]
            user_uid = data[2]
            user_gid = data[3]
            user_home = data[5]
            user_shell = data[6]

            if (user_shell != "/sbin/nologin" and
                user_shell != "/usr/sbin/nologin" and
                user_shell!= "/bin/false" and
                user_shell!= "/nonexistent"):

                user = self.User(user_name, user_shell, user_home, user_uid, user_gid)
                self.users.append(user)

                # valid accounts with no password in shadow file
                if passwd_in_shadow != "x":
                    self.criticals.append("Account: {} has password in passwd: {}".format(user, passwd_in_shadow))

                # login permitted as root
                # @to nzo: wat ??
                if user_name == "root":
                    self.warnings.append("Root account: login is permitted")

            # multiple uid 0 users
            if user_name != "root" and user_uid == "0":
                self.criticals.append("Another non root account has UID 0: %s" % user_name)

            if user_name != "root" and user_gid == "0":
                self.criticals.append("Another non root account has GID 0: %s" % user_name)

    #tests on the whole passwd file
    def checks_whole_shadow(self,data):
        return

    #tests on every line of passwd
    def checks_line_shadow(self,data):
        self.test_LIN_GEN_ACC_05(data)
        self.test_LIN_GEN_ACC_06(data)
        self.test_LIN_GEN_ACC_07(data)


    #def checks_files(self,file_passwd,file_shadow):
        #pass
        #self.test_LIN_GEN_ACC_08(file_passwd,file_shadow)


    #test LIN_GEN_ACC_04 : multiple users with same uid
    def test_LIN_GEN_ACC_04(self, data):
        list = data.split("\n")
        list_uid=[]

        for line in list:
            if len(line) > 1:
                list_uid.append(line.split(":")[2])

        seen = set()
        seen2 = set()
        for item in list_uid:
            if item in seen:
                seen2.add(item)
            else:
                seen.add(item)

        for i in seen2:
            self.warnings.append("Multiple accounts with UID %s have been found" % i)

    #test LIN_GEN_ACC_05 : check for expiration date on accounts
    def test_LIN_GEN_ACC_05(self, data):
        if data[4] == "99999" and data[1] !="*" and data[1] != "!":
            self.warnings.append("Account %s does not have a password expiration date" % data[0])

    #test LIN_GEN_ACC_06 : check for passwordless accounts
    def test_LIN_GEN_ACC_06(self, data):
        if data[1] == "":
            self.criticals.append("Account %s does not have a password" % data[0])

    # test LIN_GEN_ACC_07 : check for crypt hashing method
    def test_LIN_GEN_ACC_07(self, data):
        if data[1][0:2] == "$1":
            self.criticals.append("Account %s use MD5 hashing algorithm" % data[0])
        elif data[1][0:2] == "$5":
            self.infos.append("Account %s use SHA-256 hashing algorithm" % data[0])
        elif data[1][0:2] == "$3":
            self.warnings.append("Account %s use NTHASH hashing algorithm" % data[0])
        else:
            if len(data[1]) == 13:
                self.criticals.append("Account %s use DES hashing algorithm" %data[0])


    #def test_LIN_GEN_ACC_08(self,file_passwd,file_shadow):
    #    pass
    #    self.logger.debug("script needs pwck command access")
    #    try :
    #        res = subprocess.check_output("sudo pwck -q -r "+file_passwd+" "+file_shadow,stderr=subprocess.STDOUT,shell=True, universal_newlines=True)
    #    except subprocess.CalledProcessError as exc :
    #        self.logger.error("[ERROR] passwd or shadow file is not well formed :")
    #        data=exc.output.split('\n')
    #        for i in data:
    #            if re.match("^add user",i):
    #                self.logger.error("    user %s is invalid" % re.search("'(.*?)'",i).group(0))


    #test LIN_GEN_ACC_XX
    #define a chkgrp like?
    #'''
    #def test_LIN_GEN_ACC_08XX(self):
    #define a grpck like?
    #    subprocess.call(["sudo","grpck","-rs",""])
    #'''
