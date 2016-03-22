"""
    `try` - Awesome cli tool to try out python packages.

    This module contains the command line interface.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""


import re
import sys
import click
import tempfile

from .core import Package, try_packages


def normalize_python_version(ctx, param, value):  # pylint: disable=unused-argument
    """Normalize given python version."""
    if value is None:
        return "python{major}.{minor}".format(
            major=sys.version_info.major,
            minor=sys.version_info.minor)

    if re.match(r"\d\.\d", value):
        return "python{0}".format(value)

    return value


def fix_packages(ctx, param, value):
    """Fix value of given packages."""
    if not value:
        return None

    def fix_package(value):
        """Fix name of package."""
        if re.match("[^/]+?/[^/]+?", value):
            return Package(value.split("/")[-1], "git+git://github.com/{0}".format(value))

        return Package(value, value)

    return [fix_package(x) for x in value]


@click.command()
@click.argument("packages", nargs=-1, callback=fix_packages)
@click.option("-p", "--python", callback=normalize_python_version,
              help="The python version to use.")
@click.option("--ipython", "use_ipython", flag_value=True,
              help="Use ipython instead of python.")
def cli(packages, python, use_ipython):
    """Easily try out python packages."""
    if not packages:
        raise click.BadArgumentUsage("At least one package is required.")

    click.echo("==> Use python {0}".format(click.style(python, bold=True)))
    click.echo("[*] Downloading packages: {0}".format(click.style(",".join(p.url for p in packages), bold=True)))
    logfile = tempfile.NamedTemporaryFile(prefix="try-", suffix=".log", delete=False)
    logfile.close()
    if not try_packages(packages, python, use_ipython, logfile=logfile.name):
        click.secho("[*] Failed to try package. See {0} for more details.".format(logfile.name), fg="red")
        sys.exit(1)


main = cli

if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
