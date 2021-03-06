# -*- coding: utf-8 -*-
#
# This file is part of Radicale Server - Calendar Server
# Copyright © 2012 Guillaume Ayoub
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radicale.  If not, see <http://www.gnu.org/licenses/>.
import codecs
import os 
import pwd
import posixpath

from radicale import config, ical
from radicale.storage import filesystem

'''
Created on 15 juin 2012
Filesystem storage_per_user backend.

@author: ggentile
'''

# This function overrides the builtin ``open`` function for this module
# pylint: disable=W0622
def open(path, mode="r"):
    """Open a file at ``path`` with encoding set in the configuration."""
    abs_path = os.path.join(Collection.get_folder(path), path.replace("/", os.sep))
    return codecs.open(abs_path, mode, config.get("encoding", "stock"))
# pylint: enable=W0622


class Collection(filesystem.Collection):
    """Collection storend in a flat ical file in the user's home directory"""
    
    @property
    def _path(self):
        """Absolute path of the file at local ``path``."""
        return os.path.join(self.get_folder(self.path), self.path.replace("/", os.sep))
    
    @classmethod
    def get_owner(cls, path):
        split_path = path.split("/")
        return split_path[0]
    
    @classmethod
    def get_folder(cls, path):
        home = pwd.getpwnam(cls.get_owner(path))[5]
        return home + config.get("storage", "filesystem_folder")[1:]
    
    @classmethod
    def children(cls, path):
        abs_path = os.path.join(cls.get_folder(path), path.replace("/", os.sep))
        _, directories, files = next(os.walk(abs_path))
        for filename in directories + files:
            rel_filename = posixpath.join(path, filename)
            if cls.is_node(rel_filename) or cls.is_leaf(rel_filename):
                yield cls(rel_filename)

    @classmethod
    def is_node(cls, path):
        abs_path = os.path.join(cls.get_folder(path), path.replace("/", os.sep))
        return os.path.isdir(abs_path)

    @classmethod
    def is_leaf(cls, path):
        abs_path = os.path.join(cls.get_folder(path), path.replace("/", os.sep))
        return os.path.isfile(abs_path) and not abs_path.endswith(".props")

ical.Collection = Collection