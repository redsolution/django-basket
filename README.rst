=============
django-basket
=============

Generic basket

Installation:
=============

1. Put ``basket`` to ``INSTALLED_APPS`` in your ``settings.py`` within your django project.

2. Add ``basket.middleware.BasketMiddleware`` to ``MIDDLEWARE_CLASSES`` in your ``settings.py``.

3. Add basket to ``urlpatterns`` in your ``urls.py``::

    urlpatterns += patterns('', (r'^basket/', include('basket.urls')))

4. Sync your database::

    ./manage.py syncdb

5. Copy or symlink ``media/basket`` to your ``media`` folder.

Usage:
======

In template:
------------

First of all, load the seo_tags in every template you want to use basket::

    {% load basket_tags %}
    
Add panel with summary information to each template::

    {% show_basket_panel %}
    
Add buttons for each item to make them addable to the basket::

    {% add_basket_button <object> %}

Import ``media/basket/js/jquery-1.4.2.min.js`` from all tempalates where you are use basket::

    <script type="text/javascript" src="/media/basket/js/jquery-1.4.2.min.js"></script>

Also, please check for import ``jquery.js`` from ``basket/basket.html``.

Custom:
-------

You can specify custom models and forms to store order information.
For more information check settings in ``basket/settings.py``.

Example:
========

``settings.py``::
    INSTALLED_APPS = (
        ...
        'basket',
    )

    MIDDLEWARE_CLASSES = [
        ...
        'basket.middleware.BasketMiddleware',
    )

``urls.py``:
    urlpatterns += patterns('',
        (r'^basket/', include('basket.urls')),
    )

``templates/list.html``::
    {% load basket_tags %}
    <html>
        <head>
            <script type="text/javascript" src="/media/basket/js/jquery-1.4.2.min.js"></script>
        </head>
        <body>
            <div id="head">{% show_basket_panel %}</div>
            {% for object in objects %}
                <div>{{ object.name }}{% add_basket_button object %}
            {% endfor %}
        </body>
    </html>
