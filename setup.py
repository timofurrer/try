# -*- coding: utf-8 -*-

"""
    Setup try package.

    Only support Python versions > 3.4.1
"""

import ast
import re
import sys

from setuptools import setup, find_packages
from pip.req import parse_requirements

if sys.version_info < (3, 4, 1):
    raise RuntimeError("try requires Python 3.4.1+")


def get_version():
    """Gets the current version"""
    _version_re = re.compile(r"__VERSION__\s+=\s+(.*)")
    with open("try/__init__.py", "rb") as init_file:
        version = str(ast.literal_eval(_version_re.search(
            init_file.read().decode("utf-8")).group(1)))
    return version


setup(
    name="try",
    version=get_version(),
    license="MIT",

    description="Awesome cli tool to try out python packages",

    author="Timo Furrer",
    author_email="tuxtimo@gmail.com",

    url="https://github.com/timofurrer/try",

    packages=find_packages(),
    include_package_data=True,

    install_requires=list(x.name for x in parse_requirements("./requirements.txt")),

    entry_points={
        "console_scripts": [
            "try=try.__main__:main",
        ]
    },

    keywords=[
        "try", "python", "packages",
        "pypi", "github",
        "interactive", "console",
        "ipython", "versions",
        "virtualenv"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
)
