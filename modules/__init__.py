"""ERP01 module package.

The shared :class:`BaseModule` lives in :mod:`modules.base` and is
re-exported here so both ``from modules import BaseModule`` and
``from modules.base import BaseModule`` keep working while new feature
modules can be dropped into this package without shadowing the base.
"""

from modules.base import BaseModule

__all__ = ["BaseModule"]
