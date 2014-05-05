# -*- coding: utf-8 -*-
"""
example.main.py

"""

import webapp2

from routes import routes
from config import config

# --------------------------------------------------------------------
# App
# --------------------------------------------------------------------

app = webapp2.WSGIApplication(routes=routes, config=config, debug=True)
app.set_globals(app=app)
