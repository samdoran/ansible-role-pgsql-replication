# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils._text import to_native


def parse_psql_version(version_string):
    """Take the raw output of psql --version and return major.minor version string

    Example output from psql --version
    psql (PostgreSQL) 9.6.12
    psql (PostgreSQL) 10.7
    """
    to_native(version_string)
    version = version_string.split(' ')[-1]
    return '.'.join(version.split('.')[:2])


class FilterModule:
    def filters(self):
        return {
            'pgsql_version_string': parse_psql_version,
        }
