"""
    `try` - Awesome cli tool to try out python packages.

    This module contains the configuration parsing for try.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""

import sys
import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


PY2 = sys.version_info.major == 2


# function for compatibility
def get_option(parser_func, section, option, default=None):
    """Get config value from the given
    section and option.

    :param func parser_func: the config parser function to get the option.
    :param str section: the config section name.
    :param str option: the config option name.
    :param default: the default value if the given option in the given section
                    is not found.
    """
    if PY2:
        try:
            return parser_func(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    else:
        return parser_func(section, option, fallback=default)


def parse_config(configfile):
    """Parse the given config file and
    return configuration settings as a dictionary
    for further use.

    :param str configfile: the path to the configuration file.

    :returns: parsed configuration values.
    :rtype: dict
    """
    parser = configparser.ConfigParser()
    parser.read(configfile)

    config = {
        "python": get_option(parser.get, "env", "python"),
        "shell": get_option(parser.get, "env", "shell"),
        "keep": get_option(parser.getboolean, "env", "keep", default=False),
        "use_editor": get_option(parser.getboolean, "env", "always_use_editor", default=False),
        "tmpdir": os.path.expanduser(os.path.expandvars(get_option(parser.get, "env", "tmpdir", default="")))
    }
    return config
