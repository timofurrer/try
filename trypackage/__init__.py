"""
    `try` - Awesome cli tool to try out python packages.

    :copyright: (c) by Timo Furrer
    :license: MIT, see LICENSE for details
"""

from .core import try_packages, TryError, Package


__VERSION__ = "0.3.0"
__all__ = ["try_packages", "TryError", "Package"]
