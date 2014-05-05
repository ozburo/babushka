# -*- coding: utf-8 -*-
"""
example.basehandler.py

"""

from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2

# --------------------------------------------------------------------
# Base Handler
# --------------------------------------------------------------------

class BaseHandler(RequestHandler):

    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2()

    def render_template(self, template, **context):
        return self.jinja2.render_template(template, **context)

    def render_response(self, _template, **context):
        self.response.write(self.jinja2.render_template(_template, **context))
