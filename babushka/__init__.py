# -*- coding: utf-8 -*-
"""
    babushka
    ~~~~~~~~

    Russian Doll Caching for Jinja2 & NDB on GAE.

    :license: MIT License, see LICENSE for more details.
    :documentation: See README.md for documentation.

"""

__version__ = '1.0'

from extension import BabushkaExtension, babushka, cache
from model import BabushkaModel
