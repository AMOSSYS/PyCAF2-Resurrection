# -*- coding: utf8 -*-

from pycaf2.lib import Logger

class Module(object):

    def __init__(self):
        self.name = "Base module"
        self.logger = Logger.getLogger(__name__)

        # Results are classified in 4 categories so we can treat them afterwards
        # infos: global information on the configuration
        # improvements: improvements that can be added to have a better configuration
        # warnings: warnings that can be problematic in some point
        # criticals: warnings that are critical from a security point of view
        self.infos = []
        self.improvements = []
        self.warnings = []
        self.criticals = []

    # The logger can’t be pickled. In order to get around this, we need to
    # override the __getstate__ and __setstate__ methods to respectively
    # remove and add the logger to/from the class dict.
    def __getstate__(self):
        d = dict(self.__dict__)
        #self.logger.debug("Logger getting deleted")
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.logger = Logger.getLogger(__name__)
        #self.logger.debug("Logger Recreated")


    def run(self, server):
        """ Module main method
        """
        raise NotImplementedError

    def get_infos(self):
        if self.infos:
            return self.infos
        return []

    def get_improvements(self):
        if self.improvements:
            return self.improvements
        return []

    def get_warnings(self):
        if self.warnings:
            return self.warnings
        return []

    def get_criticals(self):
        if self.criticals:
            return self.criticals
        return []

    def to_string(self):
        res = "\n## General informations:\n"
        for i in self.infos:
            res += i+"\n"

        res += "\n## Improvements:\n"
        for j in self.improvements:
            res += j+"\n"

        res += "\n## Warnings:\n"
        for k in self.warnings:
            res += k+"\n"

        res += "\n## Critical warnings:\n"
        for k in self.criticals:
            res += k+"\n"

        return res

    def print_res(self):
        for i in self.get_infos():
            if "##" in i[:2]: # Pretty printing when we have markdown
                self.logger.info("\n{}".format(i))
            else:
                self.logger.info("[INFO] {}".format(i))
        for i in self.get_improvements():
            if "##" in i[:2]: # Pretty printing when we have markdown
                self.logger.info("\n{}".format(i))
            else:
                self.logger.info("[IMPROVEMENT] {}".format(i))
        for i in self.get_warnings():
            if "##" in i[:2]: # Pretty printing when we have markdown
                self.logger.warning("\n{}".format(i))
            else:
                self.logger.warning("[WARNING] {}".format(i))
        for i in self.get_criticals():
            if "##" in i[:2]: # Pretty printing when we have markdown
                self.logger.error("\n{}".format(i))
            else:
                self.logger.error("[CRITICAL] {}".format(i))
