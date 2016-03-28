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
context.failed = False


class TryError(Exception):
    """Try specific exception."""
    def __init__(self, msg):
        super(TryError, self).__init__(msg)
        context.failed = True


def try_packages(packages, virtualenv=None, python_version=None, shell=None, use_editor=False, keep=False, tmpdir_base=None):
    """Try a python package with a specific python version.

    The python version must already be installed on the system.

    :param str package: the name of the package to try.
    :param str virtualenv: the path to the virtualenv to use. If None a new one is created.
    :param str python_version: the python version for the interpreter.
    :param str shell: use different shell then default python shell.
    :param bool use_editor: use editor instead of interpreter.
    :param bool keep: keep try environment files.
    :param str tmpdir_base: the location for the temporary directory.
    """
    with use_temp_directory(tmpdir_base, keep) as tmpdir:
        with use_virtualenv(virtualenv, python_version):
            for package in packages:
                pip_install(package.url)

            if shell and not shell == "python":
                # shell could contain cli options: only take first word.
                pip_install(shell.split()[0])

            if not use_editor:
                shell = shell if shell else "python"
                with use_import([p.import_name for p in packages]) as startup_script:
                    run_shell(shell, startup_script)
            else:
                with use_template([p.import_name for p in packages]) as template:
                    run_editor(template)
        return tmpdir


@contextlib.contextmanager
def use_temp_directory(tmpdir_base=None, keep=False):
    """Creates a temporary directory for the virtualenv."""
    if tmpdir_base:
        if not os.path.exists(tmpdir_base):
            os.makedirs(tmpdir_base)
        prefix = os.path.join(tmpdir_base, "try-")
    else:
        prefix = "try-"

    try:
        path = tempfile.mkdtemp(prefix=prefix)
        context.tempdir_path = path
        context.logfile = os.path.join(context.tempdir_path, "logs")
        yield path
    finally:
        if not keep and not context.failed:
            shutil.rmtree(path)
        context.tempdir_path = None


@contextlib.contextmanager
def use_virtualenv(virtualenv, python_version):
    """Use specific virtualenv."""
    try:
        if virtualenv:
            # check if given directory is a virtualenv
            if not os.path.join(virtualenv, "bin/activate"):
                raise TryError("Given directory {0} is not a virtualenv.".format(virtualenv))

            context.virtualenv_path = virtualenv
            yield True
        else:
            proc = Popen("virtualenv env -p {0} >> {1}".format(python_version, context.logfile),
                         shell=True, cwd=context.tempdir_path)
            context.virtualenv_path = os.path.join(context.tempdir_path, "env")
            yield proc.wait() == 0
    finally:
        context.virtualenv_path = None


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
def use_template(packages):
    """Create a python template file importing the given packages.

    :param list packages: the name of the packages to import

    :returns: the path to the created tempkate file
    :rtype: str
    """
    with open(os.path.join(os.path.dirname(__file__), "script.template")) as template_file:
        template = template_file.read()

    template_path = os.path.join(context.tempdir_path, "main.py")
    with open(template_path, "w+") as template_file:
        template_file.write(template.format("\n".join("import {0}".format(p) for p in packages)))
    yield template_path


def pip_install(package):
    """Install given package in virtualenv."""
    exec_in_virtualenv("python -m pip install {0} >> {1}".format(package, context.logfile))


def run_shell(shell, startup_script):
    """Run specific python shell."""
    exec_in_virtualenv("PYTHONSTARTUP={0} {1}".format(startup_script, shell))


def run_editor(template_path):
    """Run editor and open the given template file."""
    editor = os.environ.get("EDITOR", "editor")
    exec_in_virtualenv("{0} {1} && python {1}".format(editor, template_path))


def exec_in_virtualenv(command):
    """Execute command in virtualenv."""
    proc = Popen(". {0}/bin/activate && {1}".format(context.virtualenv_path, command), shell=True)
    if proc.wait() != 0:
        raise TryError("Command '{0}' exited with error code: {1}. See {2}".format(
            command, proc.returncode, context.logfile))
