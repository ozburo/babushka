# -*- coding: utf-8 -*-
"""
example.models.py

"""

from google.appengine.ext.ndb import model

from babushka.model import BabushkaModel

# --------------------------------------------------------------------
# Blog Model
# --------------------------------------------------------------------

class Blog(BabushkaModel):
    name    = model.StringProperty(required=True)

    @property
    def latest_posts(self):
        return Post.query().filter(Post.blog==self.key).order(-Post.updated)

# --------------------------------------------------------------------
# Post Model
# --------------------------------------------------------------------

class Post(BabushkaModel):
    blog    = model.KeyProperty(kind='Blog', required=False)
    title   = model.StringProperty(required=True)
    body    = model.TextProperty(required=True)

    _cache_break = 'blog'

    #: alternative syntax style
    class Babushka:
        cache_break = 'blog'
