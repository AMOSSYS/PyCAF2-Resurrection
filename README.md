# PyCAF-Resurrection

## Installation

### Pip3 and Virtual environment
```
# Install python3 et pip3
apt-get install python3 python3-pip

# Install virtualenv wrapper
pip3 install virtualenvwrapper

# Configure virtualenvwrapper
mkdir ~/virtualenvs
export WORKON_HOME=~/virtualenvs
source /etc/bash_completion.d/virtualenvwrapper
export PIP_VIRTUALENV_BASE=~/virtualenvs

# Start virtualenv PyCAF2-Resurrection and install PyCAF2-Resurrection requirements
mkvirtualenv --python=/usr/bin/python3 -a $HOME/PyCAF2-Resurrection -r requirements.txt PyCAF2-Resurrection

# To exit virtualenv: $deactivate
# To remove virtualenv: $rmvirtualenv PyCAF2
# To continue working on PyCAF2-Resurrection: $workon PyCAF2-Resurrection
```

## Run

PyCAF2-Resurrection is divided in two modules:
* A web interface which allows auditors to visualize results of PyCAF2 and launch further analyses;
* The PyCAF2 core module which contains all the intelligence of servers' parsing.

### Help :

#### PyCAF2

```
Usage: launch_pycaf2.py [-h] -f FILE [--config_file CONFIG_FILE] [-i] [-s]

PyCAF2 - Codename Resurrection

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  dump file (ex : dump1.tar.bz2). Specify a folder if
                        you want to skip the extraction.
  --config_file CONFIG_FILE
                        path to the configuration file (see server.conf for
                        example)
  -i, --interactive     start interactive ipython console after PyCAF work
  -s, --pickle-to       store server object into pickle file 'server.pickle'
```

#### PyCAF2-web

```
python3 launch_web.py
```

## What the heck is PyCAF2?

PyCAF is a Configuration Audit Framework developped in Python3, which helps auditors during their work. It is the continuation of the project PyCAF which was presented at SSTIC 2015 (in french) - https://www.sstic.org/media/SSTIC2015/SSTIC-actes/utilisation_du_framework_pycaf_pour_laudit_de_conf/SSTIC2015-Slides-utilisation_du_framework_pycaf_pour_laudit_de_configuration-olivier.pdf

The architecture between PyCAF and PyCAF2 has been completely reworked. Analysed modules are now auto-loaded which means that a analysis module is a lot easier to develop (see the next section below). When dealing with an extracted server, PyCAF2 will try to detect automatically the type and version of the server's system. It is however possible to skip this discovery and directly set this with the configuration file (option --config_file).

In PyCAF2, when a server configuration is parsed and analyzed, a server object is built so we can further interact with. An ipython shell could be obtained with the parameter "-i", and a pickled server can be created so we can reimport it later if necessary (parameter "-s"). As an example, PyCAF2 results won't tell the auditor which are the packages that are up to date. It is however possible to know this by opening an ipython interpreter and parse the corresponding module:

```
$ python3 launch_pycaf2.py -f pycaf2/test/resources/linux/PC-77 -i
Python 3.5.2 (default, Nov 17 2016, 17:05:23)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.1.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: packages_module = server.get_module("Packages")
In [2]: packages_module.uptodate_packages
Out[2]:
OrderedDict([('accountsservice', '0.6.37-3+b1'),
             ('acl', '2.2.52-2'),
             ('acpi', '1.7-1'),
             ('acpi-support-base', '0.142-6'),
             ('acpid', '1:2.0.23-2'),
             ('adduser', '3.113+nmu3'),
             ('adwaita-icon-theme', '3.14.0-2'),
             ('aisleriot', '1:3.14.1-1'),
             ('alsa-base', '1.0.27+1'),
             ('alsa-utils', '1.0.28-1'),
             ('anacron', '2.3-23'),
             ('apg', '2.2.3.dfsg.1-2'),
             ('apt', '1.0.9.8.4'),
             ('apt-listchanges', '2.85.13+nmu1'),
[...]
```

### PyCAF2 outputs example

PyCAF2 logs debug output to console and audit results in the log file named "output.log".
The output.log contains the same information than console, but with a debug level set to INFO. The console output also gives information about files and lines in order to make the debug easier.
An example of console output is given below:

```
python3 launch_pycaf2.py -f pycaf2/test/resources/linux/PC-77
[MainProcess/pycaf.py:76/DEBUG] 328: Filename is: pycaf2/test/resources/linux/PC-77
[MainProcess/pycaf.py:87/DEBUG] 328: Detected that dumpfile is a directory.
[MainProcess/pycaf.py:93/INFO] 328: Analyzing pycaf2/test/resources/linux/PC-77 (2017-09-15 11:44)
[MainProcess/extract.py:37/INFO] 328: Do not to decompress anything. Using folder pycaf2/test/resources/linux/PC-77.
[MainProcess/pycaf.py:154/DEBUG] 403: OS dump informations
[MainProcess/system.py:65/DEBUG] 403: Trying to identify OS...
[MainProcess/system.py:256/DEBUG] 403: Calculating score for debian
[MainProcess/system.py:322/DEBUG] 405: Score is: 100
[MainProcess/system.py:196/DEBUG] 405: Calculating score for generic Linux
[MainProcess/system.py:244/DEBUG] 408: Score is: 99
[MainProcess/system.py:183/DEBUG] 408: Calculating score for CentOS
[MainProcess/system.py:184/DEBUG] 408: Not implemented yet
[MainProcess/system.py:86/DEBUG] 408: Calculating score for windows
[MainProcess/system.py:105/DEBUG] 410: Score is: 0
[MainProcess/system.py:75/INFO] 410:
## OS detection :
[MainProcess/system.py:77/INFO] 410: debian : 100%
[MainProcess/system.py:77/INFO] 410: generic : 99%
[MainProcess/system.py:77/INFO] 410: centos : 0%
[MainProcess/system.py:77/INFO] 410: windows : 0%
[MainProcess/pycaf.py:161/DEBUG] 411: Detection results for UUID: 6abff3ff-5684-43fa-b741-c09f9f3149d2
[MainProcess/pycaf.py:164/DEBUG] 411: Os: debian
[MainProcess/pycaf.py:164/DEBUG] 411: Code name: jessie
[MainProcess/pycaf.py:164/DEBUG] 411: Kernel: 3.16.0-4-amd64
[MainProcess/pycaf.py:164/DEBUG] 411: Arch: x64
[MainProcess/pycaf.py:164/DEBUG] 411: Distribution: debian
[MainProcess/pycaf.py:164/DEBUG] 411: System type: linux
[MainProcess/pycaf.py:167/DEBUG] 411: Analyzing debian extracted archive...
[MainProcess/server.py:49/DEBUG] 411: Loading available modules for system: linux
[MainProcess/server.py:67/DEBUG] 412: Module name is: pycaf2.modules.linux.debian.Packages
[MainProcess/server.py:67/DEBUG] 435: Module name is: pycaf2.modules.linux.generic.SSH
[MainProcess/server.py:67/DEBUG] 437: Module name is: pycaf2.modules.linux.generic.Network
[MainProcess/server.py:67/DEBUG] 437: Module name is: pycaf2.modules.linux.generic.Accounts
[MainProcess/server.py:67/DEBUG] 439: Module name is: pycaf2.modules.linux.generic.Sudoers
[MainProcess/pycaf.py:171/DEBUG] 440: Loading module: Packages
[MainProcess/pycaf.py:173/INFO] 440:
## Packages
[MainProcess/Packages.py:111/DEBUG] 445: Found URL http://ftp.fr.debian.org/debian/ for jessie
[MainProcess/Packages.py:113/DEBUG] 445: Found jessie
[MainProcess/Packages.py:111/DEBUG] 445: Found URL http://ftp.fr.debian.org/debian/ for jessie-updates
[MainProcess/Packages.py:113/DEBUG] 445: Found jessie-updates
[MainProcess/Packages.py:111/DEBUG] 445: Found URL https://apt.dockerproject.org/repo/ for debian-jessie
[MainProcess/Packages.py:113/DEBUG] 445: Found debian-jessie
[MainProcess/Packages.py:127/ERROR] 445: Found line "deb https://apt.dockerproject.org/repo/ debian-jessie main" in sources.list. Check it out manually.
[MainProcess/Packages.py:296/DEBUG] 460: distrib distribution packages that will be check: ['jessie', 'jessie-updates']
[MainProcess/Packages.py:298/DEBUG] 460: distrib jessie packages analysis in progress...
[MainProcess/Packages.py:186/DEBUG] 460: Getting URL: https://packages.debian.org/jessie/allpackages?format=txt.gz
[MainProcess/Packages.py:199/DEBUG] 1221: Downloading temporary files in /tmp/tmp6qf1s2um
[MainProcess/Packages.py:234/DEBUG] 1452: Comparing version for distrib: jessie
[MainProcess/Packages.py:361/DEBUG] 8079: Found 1431 packages up to date on jessie
[MainProcess/Packages.py:186/DEBUG] 8081: Getting URL: https://packages.debian.org/jessie-updates/allpackages?format=txt.gz
[MainProcess/Packages.py:199/DEBUG] 8425: Downloading temporary files in /tmp/tmphjqezif4
[MainProcess/Packages.py:234/DEBUG] 8440: Comparing version for distrib: jessie-updates
[MainProcess/Packages.py:366/DEBUG] 8665: Found 211 obsoletes packages
[MainProcess/module.py:85/INFO] 8666: [INFO] URLs define in sources.list are: ['http://ftp.fr.debian.org/debian/']
[MainProcess/module.py:85/INFO] 8666: [INFO] Number of up to date packages: 1431
[MainProcess/module.py:95/WARNING] 8666: [WARNING] Packages unknown(2): OrderedDict([('docker-engine', '1.13.0-0~debian-jessie'), ('linux-image-3.16.0-4-amd64', '3.16.39-1')])
[MainProcess/module.py:100/ERROR] 8666: [CRITICAL] Packages obsoletes(211): OrderedDict([('bind9-host', '1:9.9.5.dfsg-9+deb8u9'), ('debian-archive-keyring', '2014.3'), ('dnsutils', '1:9.9.5.dfsg-9+deb8u9'), ('host', '1:9.9.5.dfsg-9+deb8u9'), ('libbind9-90', '1:9.9.5.dfsg-9+deb8u9'), ('libdns-export100', '1:9.9.5.dfsg-9+deb8u9'), ('libdns100', '1:9.9.5.dfsg-9+deb8u9'), ('xserver-common', '2:1.16.4-1'), ('xserver-xorg-core', '2:1.16.4-1'), ('xwayland', '2:1.16.4-1')])
[MainProcess/pycaf.py:171/DEBUG] 8667: Loading module: SSHD configuration
[MainProcess/pycaf.py:173/INFO] 8667:
## SSHD configuration
[MainProcess/module.py:85/INFO] 8673: [INFO] Permit root login: no
[MainProcess/module.py:85/INFO] 8673: [INFO] Privilege separation: yes
[MainProcess/module.py:85/INFO] 8673: [INFO] Permit empty password: no
[MainProcess/module.py:85/INFO] 8673: [INFO] Protocol: 2
[MainProcess/module.py:85/INFO] 8673: [INFO] Log level : INFO
[MainProcess/module.py:85/INFO] 8673: [INFO] RSA authentication: yes
[MainProcess/module.py:85/INFO] 8673: [INFO] Pubkey authentication: yes
[MainProcess/module.py:90/INFO] 8674: [IMPROVEMENT] Port: 22 [DEFAULT]. It is recommended to change the default port.
[MainProcess/module.py:95/WARNING] 8674: [WARNING] X11 Forwarding: yes
[MainProcess/module.py:95/WARNING] 8674: [WARNING] Use PAM: yes
[MainProcess/pycaf.py:171/DEBUG] 8674: Loading module: Network configuration
[MainProcess/pycaf.py:173/INFO] 8674:
## Network configuration
[MainProcess/module.py:85/INFO] 8676: [INFO] Define interfaces are: [OrderedDict([('Name', 'docker0'), ('MAC', '02:42:9c:ca:9f:35'), ('IPv4', '172.17.0.1'), ('Mask', '255.255.0.0'), ('IPv6', '')]), OrderedDict([('Name', 'eth0'), ('MAC', 'b0:83:fe:78:56:42'), ('IPv4', '192.168.200.42'), ('Mask', '255.255.255.0'), ('IPv6', 'fe80::b283:feff:fe78:5642/64')]), OrderedDict([('Name', 'lo'), ('MAC', ''), ('IPv4', '127.0.0.1'), ('Mask', '255.0.0.0'), ('IPv6', '::1/128')])]
[MainProcess/pycaf.py:171/DEBUG] 8676: Loading module: List accounts
[MainProcess/pycaf.py:173/INFO] 8676:
## List accounts
[MainProcess/module.py:85/INFO] 8677: [INFO] Users with shells are: [{'User': 'root', 'shell': '/bin/bash', 'home': /root, 'UID': '0', 'GID': '0'}, {'User': 'sync', 'shell': '/bin/sync', 'home': /bin, 'UID': '4', 'GID': '65534'}, {'User': 'speech-dispatcher', 'shell': '/bin/sh', 'home': /var/run/speech-dispatcher, 'UID': '112', 'GID': '29'}, {'User': 'amossys', 'shell': '/bin/bash', 'home': /home/amossys, 'UID': '1000', 'GID': '1000'}, {'User': 'test1', 'shell': '/bin/bash', 'home': /home/test1, 'UID': '1001', 'GID': '1001'}, {'User': 'test2', 'shell': '/bin/bash', 'home': /home/test2, 'UID': '1002', 'GID': '0'}]
[MainProcess/module.py:95/WARNING] 8677: [WARNING] Root account: login is permitted
[MainProcess/module.py:95/WARNING] 8677: [WARNING] Account root does not have a password expiration date
[MainProcess/module.py:95/WARNING] 8678: [WARNING] Account amossys does not have a password expiration date
[MainProcess/module.py:95/WARNING] 8678: [WARNING] Account dkr does not have a password expiration date
[MainProcess/module.py:100/ERROR] 8678: [CRITICAL] Account: {'User': 'test2', 'shell': '/bin/bash', 'home': /home/test2, 'UID': '1002', 'GID': '0'} has password in passwd: secret_password
[MainProcess/module.py:100/ERROR] 8678: [CRITICAL] Another non root account has GID 0: test2
[MainProcess/pycaf.py:171/DEBUG] 8678: Loading module: Check Sudoers
[MainProcess/pycaf.py:173/INFO] 8678:
## Check Sudoers
[MainProcess/Sudoers.py:69/DEBUG] 8678: Found #includedir line: #includedir /etc/sudoers.d
[MainProcess/Sudoers.py:81/DEBUG] 8680: Found pycaf2/test/resources/linux/PC-77/etc/sudoers.d/README in folder /etc/sudoers.d
[MainProcess/Sudoers.py:81/DEBUG] 8681: Found pycaf2/test/resources/linux/PC-77/etc/sudoers.d/sudoers_tmp in folder /etc/sudoers.d
[MainProcess/Sudoers.py:89/DEBUG] 8683: Found #include line: #include /etc/sudoers.local
[MainProcess/Sudoers.py:176/DEBUG] 8684: Found Defaults secure_path entry, checking folders...
[MainProcess/Sudoers.py:185/DEBUG] 8684: Secure_path entries all good.
[MainProcess/Sudoers.py:138/DEBUG] 8684: Found alias type: User_Alias with name: OPERATORS and values: joe, mike, jude
[MainProcess/Sudoers.py:138/DEBUG] 8684: Found alias type: User_Alias with name: OTHER and values: john
[MainProcess/Sudoers.py:146/DEBUG] 8684: Found alias type: Runas_Alias with name: OP and values: root, operator
[MainProcess/Sudoers.py:146/DEBUG] 8684: Found alias type: Host_Alias with name: OFNET and values: 10.1.2.0/255.255.255.0
[MainProcess/Sudoers.py:146/DEBUG] 8685: Found alias type: Cmnd_Alias with name: PRINTING and values: /usr/sbin/lpc, /usr/bin/lprm
[MainProcess/module.py:85/INFO] 8685: [INFO] Defined aliases are: OrderedDict([('User_Alias', OrderedDict([('OPERATORS', ['joe', ' mike', ' jude']), ('OTHER', ['john'])])), ('Runas_Alias', OrderedDict([('OP', ['root', ' operator'])])), ('Host_Alias', OrderedDict([('OFNET', ['10.1.2.0/255.255.255.0'])])), ('Cmnd_Alias', OrderedDict([('PRINTING', ['/usr/sbin/lpc', ' /usr/bin/lprm'])]))])
[MainProcess/module.py:85/INFO] 8685: [INFO] Defaults: ['env_reset', 'mail_badpass', 'secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"', ':millert  !authenticate']
[MainProcess/module.py:85/INFO] 8685: [INFO] Rules: OrderedDict([('root', ['ALL=(ALL:ALL) ALL']), ('%sudo', ['ALL=(ALL:ALL) ALL']), ('user_hid', ['ALL=(ALL) NOPASSWD: ALL']), ('OPERATORS', ['ALL=ALL']), ('linus', ['ALL=(OP) ALL']), ('user2', ['OFNET=(ALL) ALL', 'ALL=(ALL) NOPASSWD: ALL']), ('user3', ['ALL= PRINTING']), ('user4', ['ALL=(ALL) ALL']), ('dgb', ['boulder = (operator) /bin/ls, /bin/kill, /usr/bin/lprm'])])
[MainProcess/module.py:95/WARNING] 8685: [WARNING] Defaults parameter is specific to a host, user, cmnd or runas. Checkout manually: Defaults:millert  !authenticate
[MainProcess/module.py:100/ERROR] 8685: [CRITICAL] The option authenticate is disabled for someone, checkout manually: :millert  !authenticate
[MainProcess/pycaf.py:181/DEBUG] 8685: Analysis of pycaf2/test/resources/linux/PC-77 is finished. Checkout log output.log for the report.
```

## Developping a new PyCAF2 module

As stated before, PyCAF2 has been thinking from a modules point of view. One can develop a new analysis module without taking care of its integration.

The following steps are needed:

* Add a new file in pycaf2/modules/<OS_NAME>/<MODULE_NAME>.py. If the module is generic for Linux systems, it can be placed in the folder generic/. When defining the new module, classname must be the same as filename (ex: in SSH.py, class SSH(Module)) and the class must inherit from pycaf2.lib.module.Module.

Every module must implement the run() method and fill in the corresponding attributes: infos, improvements, warnings and criticals. These attributes will be then automatically printed in the report logs.

In order to parse files from the extracted server, it is necessary to interact with the FileList instance of the server. You can use it as a classic list or call specials methods :

 - files.get_file(filename) : returns the full path for a specific filename
 - files.file_exists(filename) : return boolean
 - files.get_file_content(filename) : return the file content

### Example

The following example illustrates a super simple PyCAF2 module:
```
# coding: utf8

from pycaf2.lib.module import Module

class Test(Module):

    def __init__(self):
        super(Test, self).__init__()
        self.name = "Test module"

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

    def check_config(self, sshd_config_content):
        """ Check the configuration
        """
        pass
```

## Run tests
Tests' resources are available in directory pycaf2/test/resources/. You can use PyCAF2 tests to:
* run all tests available when modifying PyCAF2 core: `python3 -m unittest discover`
* run test on a specific module (test_parser in the example): `python3 -m unittest pycaf2/test/modules/linux/generic/test_ssh.py`

## TODO and BUGS
See:
