#
# Revelation
# Module for importing data from KeepassXC CSV export file
#
# Copyright (c) 2020 Mikel Olasagasti Uranga <mikel@olasagasti.info>
# Copyright (c) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import csv
import time

from revelation import data, entry
from . import base


class KeepassXCCSV(base.DataHandler):
    """
    Data handler for CSV files generated by KeepassXC.

    CSV format is defined in KeepassXC's CsvExporter.cpp

    https://github.com/keepassxreboot/keepassxc/blob/develop/src/format/CsvExporter.cpp

    CSV field description:

    Type:       Ignored
    Field 1:    Group
    Field 2:    Title
    Field 3:    Username
    Field 4:    Password
    Field 5:    URL
    Field 6:    Notes
    # since KeepassXC-2.6.2
    Field 7:    TOTP
    Field 8:    Icon
    Field 9:    Last Modified
    Field 10:   Created
    """

    name = "KeepassXC CSV"
    importer = True
    exporter = False
    encryption = False

    def import_data(self, input, password):
        " Import data from a file into the entry store"

        entrystore = data.EntryStore()

        # Maintain a hash of folder names to folder entries so we
        # can use each category encountered to create a new folder
        # by that name, or use an existing one if we've already
        # created it:
        folders = {}

        for line in input.splitlines()[1:]:
            f_csv = csv.reader([line.decode()])
            for row in f_csv:

                # Raise FormatError if we don't have all 9 fields
                # KeepasXC 2.5 to 2.6.1 has 6 fields
                # KeepasXC 2.6.2 has 10 fields
                if len(row) != 6 and len(row) != 10:
                    raise base.FormatError

                # If URL is present create WebEntry
                if row[4]:
                    new_entry = entry.WebEntry()
                    new_entry[entry.URLField] = row[4]
                else:
                    new_entry = entry.GenericEntry()

                new_entry.name = row[1]
                new_entry[entry.UsernameField] = row[2]
                new_entry[entry.PasswordField] = row[3]
                new_entry.notes = row[5]

                # TODO As Last modified and creationtime are from newer
                # keepassXC releases, set to current time for now
                new_entry.updated = time.time()

                # Create and/or add to folder
                # TODO split folder name and correctly group them
                if row[0] in folders:
                    parent = folders[row[0]]

                else:
                    folder = entry.FolderEntry()
                    folder.name = row[0]
                    parent = entrystore.add_entry(folder)
                    folders[row[0]] = parent

                # Add the entry
                entrystore.add_entry(new_entry, parent)

        return entrystore