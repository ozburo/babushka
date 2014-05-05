# -*- coding: utf-8 -*-
"""
example.config.py

"""

# --------------------------------------------------------------------
# Config
# --------------------------------------------------------------------

config = {}

config['webapp2_extras.jinja2'] = {
    'template_path': 'example/templates',
    'compiled_path': None,
    'force_compiled': False,
    'environment_args': {
        'auto_reload':  True,
        'autoescape':   True,
        'extensions':   [
            'jinja2.ext.autoescape',
            'jinja2.ext.with_',
            'babushka.cache',
            ],
        },
    'globals': {
        'uri_for': 'webapp2.uri_for',
        },
    'filters': {
        },
    }
