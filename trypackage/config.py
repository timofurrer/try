"""
    `try` - Awesome cli tool to try out python packages.

    This module contains the configuration parsing for try.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""

import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


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
        "python": parser.get("env", "python", fallback=None),
        "shell": parser.get("env", "shell", fallback=None),
        "keep": parser.getboolean("env", "keep", fallback=False),
        "use_editor": parser.getboolean("env", "always_use_editor", fallback=False),
        "tmpdir": os.path.expanduser(os.path.expandvars(parser.get("env", "tmpdir", fallback="")))
    }
    return config
