# Babushka

Russian Doll Caching for Jinja2 & NDB on Google App Engine.

#
## Introduction

Babushka is a take on the Russian Doll Caching pattern for Google App Engine's Python runtime environment.

The intent is to allow your app to store and retrieve its rendered template output via Memcache while offering a
convenient method to break the cache and avoid stale data.

The beauty of this design lies in its ability to nest your templates in "cached blocks" whilst forcing only those
elements that have been updated to be recached.

#
## Installing

To use Babushka in your app, simply include the `babushka` folder in your app `libs` folder, or wherever you
keep your third-party libraries.

The rest of this distribution includes an `example` app that you're free to reference.

#
## Dependencies

* [Jinja2](http://jinja.pocoo.org/docs/)
* [NDB](https://developers.google.com/appengine/docs/python/ndb/)
* [Webapp2](http://webapp-improved.appspot.com/) *example usage*

All are available as third-party libraries as part of the
[App Engine Python 2.7 runtime](https://developers.google.com/appengine/docs/python/tools/libraries27).

See `app.yaml` for reference.

#
## Getting Started

Using Babushka is pretty straightforward and essentially comes in to two parts:

1. `Babuska.Extension` to add to your Jinja2 Templating Environment
2. `Babushka.Model` to subclass for your NDB Model Classes

> Note that you *do not* have to use `Babushka.Model` if you simply want to cache your templates with static keys

#
### Using the Babushka Template Tag

There are a number of ways to configure your Jinja2 Environment based on your framework of choice.

With Webapp2 we simply add our extension using the convenient `webapp2_extras.jinja2` configuration hook.

```python

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

```

> Note that we are using `babushka.cache` instead of `babushka.BabushkaExtension` for brevity

See `example/config.py` for reference.

Once your Jinja2 environment is properly declared you can begin using the template tag.

`{% cache <cache_key> %} ... {% endcache %}`

Or if you prefer.

`{% babushka <cache_key> %} ... {% endbabushka %}`

You can also add a `timeout` parameter, in seconds, to set a hard expiration time for the block
being cached.

This isn't recommended but offered as a convenience for those using static keys and do not
want to rely of the cache key invalidation mechanism provided by our `Babushka.Model`.

`{% cache "statickey", timeout=3600 %} ... {% endcache %}`

See `example/templates/index.html` for reference.

#
### Using the Babushka Model Class

To use `Babushka.Model` simply subclass with your own NDB Model Class.

```python
class MyModel(BabushkaModel):
    name = model.StringProperty(required=True)

```

Your model entities will now have a `cache_key` attribute that you can then use as the `<cache_key>` in your
template tags.

`{% cache my_model_instance.cache_key %} ... {% endcache %}`

This cache key is based on your Model's `Kind`, a full string representation of its `Key` and a timestamp
based on its `updated` property.

> Note that `BabushkaModel` declares an "updated" DateTimeProperty to ensure that there is one for this purpose

See `example/models.py` for reference.

#
## Model Cache Key Invalidation

Since our Model's `cache_key` attribute is based on its `updated` property, every time it's saved to the
datastore its cache key will also change, thus invalidating the previously used cache key.

Because Memcache handles purging of unused keys, we don't need to worry about deleting our previously used
cache keys.

However, since we also wish to nest our templates based on *other* Model's cache keys, we also need
to invalidate those keys as well. Essentially we have to use "hooks" that trigger updates on those
related entities.

By default, any model entities that are ancestors, also update their parent entity when updated. This takes advantage
of the datastore's inherent parent/ancestor design and allows us to be a little more efficient by
fetching related entities using a Model's `Key.parent()` when we can, e.g. for deletes.

For those models that don't have a parent, but have relationships set via `KeyProperty` attributes, or both -- we can
signify which related entities we wish to update by setting the `_cache_break` property on your model:

```python
class Post(BabushkaModel):
    blog    = model.KeyProperty(kind='Blog', required=False)
    title   = model.StringProperty(required=True)
    body    = model.TextProperty(required=True)

    _cache_break = 'blog'

```

In this example the entity set to this Model's `blog` property will also be updated when this model
is created, updated or deleted.

You can also set a list of properties:

```python
class Post(BabushkaModel):
    site    = model.KeyProperty(kind='Site', required=True)
    blog    = model.KeyProperty(kind='Blog', required=False)
    title   = model.StringProperty(required=True)
    body    = model.TextProperty(required=True)

    _cache_break = ['site', 'blog']

```

Now `site` and `blog` will be updated once an operation has occurred on this model.

You can also set the `_cache_break` property with a Class style syntax if preferred.

```python
class Post(BabushkaModel):
    blog    = model.KeyProperty(kind='Blog', required=False)
    title   = model.StringProperty(required=True)
    body    = model.TextProperty(required=True)

    class Babushka:
        cache_break = 'blog'

```

> Remember that it's necessary to subclass *all* the models you use to nest your template blocks
with so that cache key invalidation can occur

#
## Template Cache Key Invalidation

Invaliding cache keys based on Model operations is great but what about when you update the
actual template itself?

Normally you would have to flush your cache to force your template changes to take effect, or
add an additional namespace variable to your cache keys to force invalidation.

This isn't necessary since `Babushka.Extension` appends a "md5 checksum" based
on the content of the template itself, as well as the template's filename and path, to the
final cache key used.

This allows you to make changes to your templates without having to worry about stale caches
or flushing the cache every time, as well as ensuring the usage of the same Model `cache_key` in different
template locations does not create any race conditions.

#
## Example

Using the canonical blog as our example, we can use Babushka to cache all the `latest_posts` of our blog
whilst breaking this cache once any of our nested posts have been updated, created, or deleted.

```html
<h1>My Blog</h1>

{% cache blog.cache_key %}

<h3>Here are my blog's latest posts:</h3>

{% for post in blog.latest_posts %}
<ul>
    {% cache post.cache_key %}
    <li>{{post.title}}</li>
    {% endcache %}
</ul>
{% endfor %}

{% endcache %}
```

Using this pattern we save having to query for our post entities every time this template is rendered and only
have to pass our blog entity to the template for rendering.

```python
class ExampleHandler(BaseHandler):

    def get(self):
        blog = Blog.get_by_id('main')
        context = {
            'blog': blog,
            }
        return self.render_response('/index.html', **context)

```

See `example` folder for a complete reference.

#
## Inspiration

Babushka is based on the "Cache Digests" feature introduced in [Rails 4](http://rubyonrails.org).

For a more detailed explanation of its concept and roots, please refer to DHH's original
blog posts [here](http://signalvnoise.com/posts/3112-how-basecamp-next-got-to-be-so-damn-fast-without-using-much-client-side-ui) and [here](http://signalvnoise.com/posts/3113-how-key-based-cache-expiration-works).

#
## License

This package is offered under the MIT License, see `LICENSE` for more details.















