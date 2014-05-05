# -*- coding: utf-8 -*-
"""
    babushka
    ~~~~~~~~

    Russian Doll Caching for Jinja2 & NDB on GAE.

    :license: MIT License, see LICENSE for more details.
    :documentation: See README.md for documentation.

"""

from google.appengine.api import memcache

from jinja2 import nodes
from jinja2.ext import Extension

import hashlib

# --------------------------------------------------------------------
# Babushka Jinja Extension
# --------------------------------------------------------------------

class BabushkaExtension(Extension):
    tags = set(['cache', 'babushka'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        body = parser.parse_statements(['name:endcache', 'name:endbabushka'], drop_needle=True)

        checksum = hashlib.md5(str(body)).hexdigest()
        args.append(nodes.Const(checksum))

        args.append(nodes.Const(parser.filename))

        return nodes.CallBlock(
            self.call_method('_cache', args), [], [], body
        ).set_lineno(lineno)

    def _cache(self, cache_key, timeout, checksum, filename, caller):
        if not cache_key:
            return caller()

        cache_key = '%s/%s/%s' % (cache_key, checksum, filename)
        value = memcache.get(cache_key)
        if not value:
            value = caller()
            memcache.add(cache_key, value, time=timeout or 0)

        return value

cache = babushka = BabushkaExtension
