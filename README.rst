==================================
MicroService framework :: Resource
==================================

.. image:: https://travis-ci.org/palankai/pyrs-resource.svg?branch=master
       :target: https://travis-ci.org/palankai/pyrs-resource

.. image:: https://coveralls.io/repos/palankai/pyrs-resource/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/palankai/pyrs-resource?branch=master

.. image:: https://readthedocs.org/projects/pyrs-resource/badge/?version=stable
   :target: http://pyrs-resource.readthedocs.org/
   :alt: Documentation Status

Project homepage: `<https://github.com/palankai/pyrs-resource>`_

Documentation: `<http://pyrs-resource.readthedocs.org>`_

Issue tracking: `<https://github.com/palankai/pyrs-resource/issues>`_

What is this package for
------------------------

In the python world there are many RESTFul framework. Some of them based on 
Django others are based on Flask. I've tried some but I had the feeling, I want
to learn one, the use with Django or Flask or even Odoo. And I don't mention
sometimes I found them not flexible enough. So, I've decided write my own
independent framework what anybody can use in at least the mentioned 3 
different worlds.

Nutshell (notice that, it would be the achivement)
--------------------------------------------------

.. code:: python

    from pyrs import resource
    from pyrs.resource import GET

    class UserResouce:

        @GET(response=ArrayOfUserSchema)
        def get_users(self):
            return User.objects.all()

        @PUT(path='/<int:user_id>', response=UserSchema, request=UserSchema)
        def update_user(self, user_id, body):
            user = get_object_or_404(User, pk=user_id)
            user.name = body['name']
            user.email = body['email']
            user.save()
            return user

    app = resource.Application()
    app.add('/user', UserResouce)

In this example I've shown Django (like) example.
The schema is based on `pyrs.schema <http://pyrs-schema.readthedocs.org/>`_.
Even if I tend to use that framework, you would be able to use any other.

Features
--------
- Using simple classes or even functions (no inheritance)
- Wrapped error handling, errors can be serialised
- Extensible API
- Works with python 2.7, 3.3, 3.4 (tested against these versions)
- Hooks for extending the dispatching process

Installation
------------

.. code:: bash

   $ pip install pyrs-resource

Dependencies
------------

See `requirements.txt` for details, but mainly depends on `Werkzeug <http://werkzeug.pocoo.org/>`_.
I'm using that project routing capabilities. Also depends on `pyrs.schema` as
I mentioned in nutshell section.

Important caveats
-----------------

This code right now really in beta state. I plan to release soon as possible
a completely working code, but right now it's just shaping.

The ecosystem
-------------

This work is part of `pyrs framework <https://github.com/palankai/pyrs>`_.
The complete framework follow the same intention to implement flexible
solution.

Contribution
------------

I really welcome any comments!
I would be happy if you fork my code or create pull requests.
I've already really strong opinions what I want to achieve and how, though any
help would be welcomed.

Feel free drop a message to me!
