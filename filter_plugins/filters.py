# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils._text import to_native

from distutils.version import LooseVersion


def parse_psql_version(version_string):
    """Take the raw output of psql --version and return major.minor version string

    Example output from psql --version
    psql (PostgreSQL) 9.6.12
    psql (PostgreSQL) 10.7
    psql (PostgreSQL) 10.6 (Ubuntu 10.6-0ubuntu0.18.04.1)
    """
    to_native(version_string)
    return re.search('[0-9]{1,}\.[0-9]{1,}',version_string).group()

def get_psql_service_name(version):
    version = to_native(version)
    if LooseVersion(version) < LooseVersion('10'):
        version = '.'.join(version.split('.')[:2])
    elif LooseVersion(version) >= LooseVersion('10'):
        version = version.split('.')[0]
    return 'postgresql-{0}'.format(version)


class FilterModule:
    def filters(self):
        return {
            'pgsql_version_string': parse_psql_version,
            'pgsql_service_string': get_psql_service_name,
        }
