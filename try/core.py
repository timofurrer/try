"""
    `try` - Awesome cli tool to try out python packages.

    This module contains the core functionality.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""

import os
import shutil
import tempfile
import contextlib
import threading
from subprocess import Popen
from collections import namedtuple


Package = namedtuple("Package", ["name", "url", "import_name"])

context = threading.local()  # pylint: disable=invalid-name
context.logfile = "logs"
context.failed = False


class TryError(Exception):
    """Try specific exception."""
    def __init__(self, msg):
        super(TryError, self).__init__(msg)
        context.failed = True


def try_packages(packages, python_version, use_ipython=False, keep=False):
    """Try a python package with a specific python version.

    The python version must already be installed on the system.

    :param str package: the name of the package to try
    :param str python_version: the python version for the interpreter
    :param bool use_ipython: use ipython as an interpreter
    :param bool keep: keep try environment files
    """
    with use_temp_directory(keep) as tmpdir:
        with use_virtualenv(python_version):
            for package in packages:
                pip_install(package.url)

            if use_ipython:
                pip_install("ipython")

            interpreter = "ipython" if use_ipython else "python"
            with use_import([p.import_name for p in packages]) as startup_script:
                run_interpreter(interpreter, startup_script)
        return tmpdir


@contextlib.contextmanager
def use_import(packages):
    """Creates the python startup file for the interpreter.

    :param list packages: the name of the packages to import

    :returns: the path of the created file
    :rtype: str
    """
    startup_script = os.path.join(context.tempdir_path, "startup.py")
    with open(startup_script, "w+") as startup_script_file:
        for package in packages:
            startup_script_file.write("import {0}\n".format(package))
        startup_script_file.flush()
        yield startup_script


@contextlib.contextmanager
def use_temp_directory(keep=False):
    """Creates a temporary directory for the virtualenv."""
    try:
        path = tempfile.mkdtemp(prefix="try-")
        context.tempdir_path = path
        yield path
    finally:
        if not keep and not context.failed:
            shutil.rmtree(path)
        context.tempdir_path = None


@contextlib.contextmanager
def use_virtualenv(python_version):
    """Use specific virtualenv."""
    try:
        proc = Popen("virtualenv env -p {0} >> {1}".format(python_version, context.logfile),
                     shell=True, cwd=context.tempdir_path)
        context.virtualenv_path = "env"
        yield proc.wait() == 0
    finally:
        context.virtualenv_path = None


def pip_install(package):
    """Install given package in virtualenv."""
    exec_in_virtualenv("python -m pip install {0} >> {1}".format(package, context.logfile))


def run_interpreter(interpreter, startup_script):
    """Run specific python interpreter."""
    exec_in_virtualenv("PYTHONSTARTUP={0} {1}".format(startup_script, interpreter))


def exec_in_virtualenv(command):
    """Execute command in virtualenv."""
    proc = Popen(". env/bin/activate && {0}".format(command), shell=True, cwd=context.tempdir_path)
    if proc.wait() != 0:
        raise TryError("Command '{0}' exited with error code: {1}. See {2}".format(
            command, proc.returncode, os.path.join(context.tempdir_path, context.logfile)))
