# -*- coding: utf-8 -*-
"""
example.routes.py

"""

from webapp2_extras.routes import HandlerPrefixRoute, RedirectRoute

# --------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------

routes = [

    HandlerPrefixRoute('example.handlers.', [

        RedirectRoute('/',
            name = 'index',
            handler = 'ExampleHandler',
            strict_slash = True,
            ),
        RedirectRoute('/populate',
            name = 'populate',
            handler = 'DebugHandler:populate',
            strict_slash = True,
            ),
        RedirectRoute('/update',
            name = 'update',
            handler = 'DebugHandler:update',
            strict_slash = True,
            ),
        RedirectRoute('/delete',
            name = 'delete',
            handler = 'DebugHandler:delete',
            strict_slash = True,
            ),

        ])

    ]
