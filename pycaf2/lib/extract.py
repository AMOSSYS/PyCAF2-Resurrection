# -*- coding: utf8 -*-

import tarfile
import zipfile
import os
import uuid
import shutil

from pycaf2.lib.file_list import FileList
from pycaf2.lib.server import Server
from pycaf2.lib import Logger

class ExtractionFail(Exception):
    """ Generic extraction exception
    """
    pass

class Extract(object):
    def __init__(self):
        self.extracted = []
        self.logger = Logger.getLogger(__name__)

    def load_file(self, filename, extract=True):
        """
        Create Server object from archive.
        If the extract arguments is set to True, don't do the extraction.
        Function has to return a dump dict() with key: folder, file_list
        """
        if filename is None:
            raise Exception("Filename is None")

        # Create Server object
        server = Server()

        if extract is False:
            # Folder is already uncompressed. Just initialize the dump dict
            self.logger.info("Do not to decompress anything. Using folder {}.".format(filename))
            server.extracted_folder = filename
            server.file_list = self.get_dump_file_list(server.extracted_folder)
            #self.logger.debug("Dump is: {}".format(dump))
            return server

        server.extracted_folder = str(uuid.uuid1())
        server.file_list = FileList()

        try:
            # Create output folder
            self.logger.debug("Creating output folder: {}".format(server.extracted_folder))
            os.mkdir(server.extracted_folder)

            self.extract_archive(filename, server.extracted_folder)
            # Get file list from extracted dump archive
            server.file_list = self.get_dump_file_list(server.extracted_folder)
        except IOError:
            if os.path.exists(server.extracted_folder):
                shutil.rmtree(server.extracted_folder)
            self.logger.error("dump file %s not found or unreadable" % filename)
            raise ExtractionFail()

        return server


    def extract_archive(self, filename, path):
        """ Recursively extract dump archive
        """
        self.logger.debug("Extracting {} in folder: {}".format(filename, path))

        # Extract dump
        if zipfile.is_zipfile(filename):
            with zipfile.ZipFile(filename, "r") as dump_zip:
                dump_zip.extractall(path)
        elif tarfile.is_tarfile(filename):
            compressed = tarfile.open(filename)
            compressed.extractall(path)

        # Get file list from extracted dump archive
        file_list = self.get_dump_file_list(path)
        try:
            file_list.remove(filename)
        except ValueError:
            # Remove key if exist, else ignore
            pass

        zip_files = []
        for file in file_list:
            try:
                if zipfile.is_zipfile(file) or tarfile.is_tarfile(file):
                    zip_files.append(file)
            except:
                # Prevent errors due to symlink and sockets
                continue

        self.extracted.append(filename)
        for zip_file in zip_files:
            if zip_file not in self.extracted:
                self.extract_archive(zip_file, os.path.split(zip_file)[0])


    def get_dump_file_list(self, path):
        """ Return every filenames from extracted dump
        """
        file_list = FileList()
        for root, directories, filenames in os.walk(path):
            for filename in filenames:
                file_list.append(os.path.join(root, filename))
        return file_list
