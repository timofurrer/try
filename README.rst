try
===
|pypi| |license|

**try** is an easy-to-use cli tool to try out python packages.

|demo|

Features
--------

- Install specific package version from PyPI
- Install package from GitHub
- Install in virtualenv using specific version of python
- Specify alternative python package import name
- Keep try environment after interactive session
- Launch interactive python console (optional ipython) with already imported package
- Launch editor instead of interpreter

Usage
-----

.. code:: bash

    try requests
    try requests --ipython
    try requests -p 3.5
    try requests -p /usr/bin/python3.4.1
    try requests==2.8.1
    try kennethreitz/requests --ipython
    try click-didyoumean:click_didyoumean  # if python package name is different then pip package name
    try requests --editor


Installation
------------

Use **pip** to install **try**:

.. code::

    pip3 install trypackage


Help
~~~~

**try** comes with an awesome CLI interface thanks to *click*.

.. code::

    Usage: try [OPTIONS] [PACKAGES]...

      Easily try out python packages.

    Options:
      -p, --python TEXT   The python version to use.
      --ipython           Use ipython instead of python.
      -k, --keep          Keep try environment files.
      --editor            Try with editor instead of interpreter.
      --version           Show the version and exit.
      --help              Show this message and exit.

**try** was inspired by https://github.com/VictorBjelkholm/trymodule.

.. |pypi| image:: https://img.shields.io/pypi/v/trypackage.svg?style=flat&label=version
    :target: https://pypi.python.org/pypi/trypackage
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat
    :target: https://raw.githubusercontent.com/timofurrer/try/master/LICENSE
    :alt: Package license

.. |demo| image:: https://asciinema.org/a/bd60nu08dbklh5d16lyd69fvx.png
    :target: https://asciinema.org/a/bd60nu08dbklh5d16lyd69fvx
    :alt: Demo
