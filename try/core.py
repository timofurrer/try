"""
    `try` - Awesome cli tool to try out python packages.

    This module contains the core functionality.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""

import shutil
import tempfile
import contextlib
from subprocess import Popen
from collections import namedtuple


Package = namedtuple("Package", ["name", "url", "import_name"])


def try_packages(packages, python_version, use_ipython=False, logfile="/dev/null", keep=False):
    """Try a python package with a specific python version.

    The python version must already be installed on the system.

    :param str package: the name of the package to try
    :param str python_version: the python version for the interpreter
    """
    with use_import([x.import_name for x in packages]) as startup_script, use_temp_directory(keep) as tmpdir:
        if use_ipython:
            interpreter = build_ipython_interpreter_cmd(startup_script, logfile)
        else:
            interpreter = build_python_interpreter_cmd(startup_script)

        cmd = "{virtualenv} && {pip_install} && {interpreter}".format(
            virtualenv=build_virtualenv_cmd(python_version, logfile),
            pip_install=build_pip_cmd([x.url for x in packages], logfile),
            interpreter=interpreter)

        with open(logfile, "a+") as log_f:
            log_f.write("cmd is: '{0}'\n".format(cmd))

        proc = Popen(cmd, shell=True, cwd=tmpdir)
        return proc.wait() == 0, tmpdir


@contextlib.contextmanager
def use_import(packages):
    """Creates the python startup file for the interpreter.

    :param list packages: the name of the packages to import

    :returns: the path of the created file
    :rtype: str
    """
    with tempfile.NamedTemporaryFile(suffix=".py") as tmpfile:
        for package in packages:
            tmpfile.write("import {0}\n".format(package).encode("utf-8"))
        tmpfile.file.flush()
        yield tmpfile.name


@contextlib.contextmanager
def use_temp_directory(keep=False):
    """Creates a temporary directory for the virtualenv."""
    try:
        path = tempfile.mkdtemp(prefix="try-")
        yield path
    finally:
        if not keep:
            shutil.rmtree(path)


def build_pip_cmd(packages, logfile):
    """Install the given packages using pip.

    :param list packages: the name of the packages
    """

    return "python -m pip install {0} > {1}".format(" ".join(packages), logfile)


def build_virtualenv_cmd(python_version, logfile):
    """Build command to create and source a
    python virtualenv using a specific python version.

    :param str python_version: the python version to use
    """
    return "virtualenv env -p {0} > {1} && . env/bin/activate".format(python_version, logfile)


def build_python_interpreter_cmd(startup_script):
    """Build command to launch python interpreter with
    already imported package.

    :param str startup_script: the script to launch on startup
    """
    return "PYTHONSTARTUP={0} python".format(startup_script)


def build_ipython_interpreter_cmd(startup_script, logfile):
    """Build command to launch ipython interpreter with
    already imported package.

    :param str startup_script: the script to launch on startup
    """
    return "{0} && PYTHONSTARTUP={1} ipython".format(build_pip_cmd(["ipython"], logfile), startup_script)
