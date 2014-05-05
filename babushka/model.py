# -*- coding: utf-8 -*-
"""
    babushka
    ~~~~~~~~

    Russian Doll Caching for Jinja2 & NDB on GAE.

    :license: MIT License, see LICENSE for more details.
    :documentation: See README.md for documentation.

"""

from google.appengine.ext.ndb import model

import time

# --------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------

class BabushkaModelError(Exception):
    pass

# --------------------------------------------------------------------
# Babushka Model
# --------------------------------------------------------------------

class BabushkaModel(model.Model):
    updated = model.DateTimeProperty(auto_now=True)

    @property
    def cache_key(self):
        return '%s/%s/%s%s' % (self.key.kind(), self.key.urlsafe(),
                time.mktime(self.updated.timetuple()), self.updated.microsecond)

    def _pre_put_hook(self):
        self.break_cache(self.key, self)
        return super(BabushkaModel, self)._pre_put_hook()

    @classmethod
    def _pre_delete_hook(cls, key):
        cls.break_cache(key)
        return super(BabushkaModel, cls)._pre_delete_hook(key)

    @classmethod
    def break_cache(cls, key, entity=None):
        keys = []

        if key.parent():
            keys.append(key.parent())

        cache_break = None
        if hasattr(cls, '_cache_break'):
            cache_break = cls._cache_break
        elif hasattr(cls, 'Babushka') and hasattr(cls.Babushka, 'cache_break'):
            cache_break = cls.Babushka.cache_break

        if cache_break:
            if not isinstance(cache_break, (list, tuple)):
                cache_break = [cache_break]

            if not entity:
                entity = key.get()

            for attr in cache_break:
                try:
                    prop = getattr(cls, attr)
                except Exception, msg:
                    raise BabushkaModelError(msg)

                if not isinstance(prop, model.KeyProperty):
                    raise BabushkaModelError("attribute '%s' must be a 'KeyProperty' not '%s'" % \
                                            (attr, prop.__class__.__name__))

                key = getattr(entity, attr)
                if key and key not in keys:
                    keys.append(key)

        entities = model.get_multi(keys)
        model.put_multi(entities)
