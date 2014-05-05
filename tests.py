# -*- coding: utf-8 -*-
"""
tests.py

"""

import os
import sys
import logging
import unittest

sys.path.insert(0, '/usr/local/google_appengine')

import dev_appserver
dev_appserver.fix_sys_path()

from google.appengine.ext import testbed
from google.appengine.ext.ndb import model
from google.appengine.ext.ndb import tasklets

from google.appengine.datastore import datastore_stub_util

from babushka import BabushkaModel, BabushkaModelError
from example.models import Blog, Post

import webapp2
import yaml
import time

# --------------------------------------------------------------------
# Base Test Case
# --------------------------------------------------------------------

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        """Set up the test framework.

        Service stubs are available for the following services:

        - Datastore (use init_datastore_v3_stub)
        - Memcache (use init_memcache_stub)
        - Task Queue (use init_taskqueue_stub)
        - Images (only for dev_appserver; use init_images_stub)
        - URL fetch (use init_urlfetch_stub)
        - User service (use init_user_stub)
        - XMPP (use init_xmpp_stub)
        """
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()

        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

        # To set custom env vars, pass them as kwargs *after* activate().
        # self.setup_env()

        # Next, declare which service stubs you want to use.
        # self.testbed.init_memcache_stub()
        # self.testbed.init_user_stub()

        # Add taskqueue support with our queue.yaml path
        # self.testbed.init_taskqueue_stub(root_path=os.path.dirname(os.path.dirname( __file__ )))

        # Create a consistency policy that will simulate the High Replication consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy, require_indexes=False)
        # self.testbed.init_datastore_v3_stub(consistency_policy=self.policy, require_indexes=True,
        #                                     root_path=os.path.dirname(os.path.dirname( __file__ )))

        # Only when testing ndb.
        self.reset_kind_map()
        self.setup_context_cache()

    def tearDown(self):
        # This restores the original stubs so that tests do not interfere
        # with each other.
        self.testbed.deactivate()
        # Clear thread-local variables.
        self.clear_globals()

    def reset_kind_map(self):
        model.Model._reset_kind_map()

    def setup_context_cache(self):
        """Set up the context cache.

        We only need cache active when testing the cache, so the default
        behavior is to disable it to avoid misleading test results. Override
        this when needed.
        """
        ctx = tasklets.get_context()
        ctx.set_cache_policy(False)
        ctx.set_memcache_policy(False)

    def clear_globals(self):
        webapp2._local.__release_local__()

    def register_model(self, name, cls):
        model.Model._kind_map[name] = cls

# --------------------------------------------------------------------
# Babushka Test Case
# --------------------------------------------------------------------

class BabushkaTestCase(BaseTestCase):

    def test_creation(self):
        self.register_model('Blog', Blog)
        self.register_model('Post', Post)

        data = yaml.load(open('example/data.yaml'))

        blog = Blog.get_or_insert(data['blog']['name'], name=data['blog']['name'])

        for post in data['blog']['posts']:
            post = Post(parent=blog.key, **post)
            post.put()

        for post in data['blog']['posts']:
            post = Post(blog=blog.key, **post)
            post.put()

    def test_bad_assignment(self):

        class Blog(BabushkaModel):
            pass

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

            _cache_break = 'badattr'

        blog = Blog.get_or_insert('main')
        post = Post(parent=blog.key, title='title')

        self.assertRaises(BabushkaModelError, post.put)

        Post._cache_break = 'title'

        post = Post(parent=blog.key, title='title')

        self.assertRaises(BabushkaModelError, post.put)

        Post._cache_break = 'blog'

        post = Post(parent=blog.key, title='title')

        post.put()

    def test_assignments(self):

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

        post = Post(title='title')
        post.put()

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

            class Babushka:
                cache_break = 'blog'

        post = Post(title='title')
        post.put()

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

            _cache_break = 'blog'

        post = Post(title='title')
        post.put()

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

            _cache_break = None

        post = Post(title='title')
        post.put()

    def test_cache_keys(self):

        class Blog(BabushkaModel):
            pass

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

        blog = Blog.get_or_insert('main')
        post = Post(parent=blog.key, title='title')
        post.put()

        old_blog_cache_key = blog.cache_key
        old_post_cache_key = post.cache_key

        post.title = 'new title'
        post.put()

        blog = Blog.get_by_id('main')

        self.assertNotEqual(blog.cache_key, old_blog_cache_key)
        self.assertNotEqual(post.cache_key, old_post_cache_key)

        class Blog(BabushkaModel):
            pass

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

        blog = Blog.get_or_insert('main')
        post = Post(blog=blog.key, title='title')
        post.put()

        old_blog_cache_key = blog.cache_key
        old_post_cache_key = post.cache_key

        post.title = 'new title'
        post.put()

        blog = Blog.get_by_id('main')

        self.assertEqual(blog.cache_key, old_blog_cache_key)
        self.assertNotEqual(post.cache_key, old_post_cache_key)

        class Blog(BabushkaModel):
            pass

        class Post(BabushkaModel):
            blog    = model.KeyProperty(kind='Blog', required=False)
            title   = model.StringProperty(required=True)

            _cache_break = 'blog'

        blog = Blog.get_or_insert('main')
        post = Post(blog=blog.key, title='title')
        post.put()

        old_blog_cache_key = blog.cache_key
        old_post_cache_key = post.cache_key

        post.title = 'new title'
        post.put()

        blog = Blog.get_by_id('main')

        self.assertNotEqual(blog.cache_key, old_blog_cache_key)
        self.assertNotEqual(post.cache_key, old_post_cache_key)

if __name__ == '__main__':
    unittest.main()
