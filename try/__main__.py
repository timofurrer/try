"""
    `try` - Awesome cli tool to try out python packages.

    This module contains the command line interface.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""


import re
import sys
import click

from .core import try_package


def normalize_python_version(ctx, param, value):  # pylint: disable=unused-argument
    """Normalize given python version."""
    if value is None:
        return "python{major}.{minor}".format(
            major=sys.version_info.major,
            minor=sys.version_info.minor)

    if re.match(r"\d\.\d", value):
        return "python{0}".format(value)

    return value


@click.command()
@click.argument("package")
@click.option("-v", "--version", callback=normalize_python_version,
              help="The python version to use.")
@click.option("--ipython", "use_ipython", flag_value=True,
              help="Use ipython instead of python.")
def cli(package, version, use_ipython):
    """Easily try out python packages."""
    click.echo("==> Use python {0}".format(click.style(version, bold=True)))
    click.echo("[*] Download {0} from PyPI".format(click.style(package, bold=True)))
    if not try_package(package, version, use_ipython):
        click.secho("[*] Failed to try package. See logs for more details.", fg="red")
        sys.exit(1)


main = cli

if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
