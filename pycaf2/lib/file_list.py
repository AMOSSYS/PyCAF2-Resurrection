# coding: utf8

import re

class FileList(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def get_file(self, filename):
        """ Get full filename
        """
        for item in self:
            if re.search(filename,item) is not None:
                return item
        return None

    def get_files_list(self, regex):
        """ Return a list of filenames that match regex
        """
        files = []
        for item in self:
            if re.search(regex, item) is not None:
                files.append(item)
        return files

    def file_exists(self, filename):
        """ Return True if file exists in dump
        """
        for item in self:
            if re.search(filename,item) is not None:
                return True
        return False

    def get_file_content(self, filename):
        """ Search file and return content
        """
        f = self.get_file(filename)
        if f is None:
            return None
        content = None
        # Always read files with UTF8 and ignore errors
        #with open(f, 'r', encoding='utf-8', errors='ignore') as fd:
        with open(f, 'rt') as fd:
            content = fd.read()
        return content
