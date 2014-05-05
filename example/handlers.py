# -*- coding: utf-8 -*-
"""
example.handlers.py

"""

from basehandler import BaseHandler

from models import Blog, Post

import yaml

# --------------------------------------------------------------------
# Example Handler
# --------------------------------------------------------------------

class ExampleHandler(BaseHandler):

    def get(self):
        blog = Blog.get_by_id('main')
        context = {
            'blog': blog,
            }
        return self.render_response('/index.html', **context)

# --------------------------------------------------------------------
# Debug Handler
# --------------------------------------------------------------------

class DebugHandler(BaseHandler):

    def populate(self):
        data = yaml.load(open('example/data.yaml'))

        blog = Blog.get_or_insert(data['blog']['name'], name=data['blog']['name'])
        for post in data['blog']['posts']:
            post = Post(blog=blog.key, **post)
            post.put()

        return self.redirect_to('index')

    def update(self):
        post = Post.query().get()
        if post:
            post.title = '%s *UPDATED*' % post.title
            post.put()

        return self.redirect_to('index')

    def delete(self):
        post = Post.query().get()
        if post:
            post.key.delete()

        return self.redirect_to('index')
