"""
    `try` - Awesome cli tool to try out python packages.

    This module contains the command line interface.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""


import os
import re
import sys
import click

from .core import Package, TryError, try_packages
from .config import parse_config


def normalize_python_version(ctx, param, value):  # pylint: disable=unused-argument
    """Normalize given python version."""
    if value is None:
        return "python{major}.{minor}".format(
            major=sys.version_info.major,
            minor=sys.version_info.minor)

    if re.match(r"\d\.\d", value):
        return "python{0}".format(value)

    return value


def resolve_packages(ctx, param, value):
    """Fix value of given packages."""
    if not value:
        return None

    def resolve_package(value):
        """Fix name of package."""
        match = re.match(r"([^/]+?/[^/:]+)(?::(.+))?", value)
        if match:  # install from github repository
            name = match.group(1)
            url = "git+git://github.com/{0}".format(match.group(1))
            import_name = match.group(2) if match.group(2) else match.group(1).split("/")[-1]
        else:  # install from PyPI
            if ":" in value:
                name, import_name = value.split(":", 1)
            else:
                name = value
                import_name = name.split("==")[0]

            url = name

        return Package(name, url, import_name.replace("-", "_"))

    return [resolve_package(x) for x in value]


@click.command(context_settings=dict(default_map=parse_config(os.path.join(click.get_app_dir("try"), "config.ini"))))
@click.argument("packages", nargs=-1, callback=resolve_packages)
@click.option("--virtualenv",
              help="Use already existing virtualenv.")
@click.option("-p", "--python", callback=normalize_python_version,
              help="The python version to use.")
@click.option("--ipython", "use_ipython", flag_value=True,
              help="Use ipython instead of python.")
@click.option("--shell",
              help="Specify the python shell to use. (This will override --ipython)")
@click.option("-k", "--keep", flag_value=True,
              help="Keep try environment files.")
@click.option("--editor", "use_editor", flag_value=True,
              help="Try with editor instead of a shell.")
@click.option("--tmpdir",
              help="Specify location for temporary directory.")
@click.version_option()
def cli(packages, virtualenv, python, use_ipython, shell, keep, use_editor, tmpdir):  # pylint: disable=too-many-arguments
    """Easily try out python packages."""
    if not packages:
        raise click.BadArgumentUsage("At least one package is required.")

    if not shell and use_ipython:
        shell = "ipython"

    click.echo("==> Use python {0}".format(click.style(python, bold=True)))
    if shell:
        click.echo("==> Use shell {0}".format(click.style(shell, bold=True)))
    click.echo("[*] Downloading packages: {0}".format(click.style(",".join(p.url for p in packages), bold=True)))

    try:
        envdir = try_packages(packages, virtualenv, python, shell, use_editor, keep, tmpdir)
    except TryError as error:
        click.secho("[*] {0}".format(error), fg="red")
        sys.exit(1)

    if keep:
        click.echo("==> Have a look at the try environment at: {0}".format(envdir))


main = cli

if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
