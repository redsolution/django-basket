=============
django-basket
=============

Installation
=============

1. Add ``basket`` to ``INSTALLED_APPS``

2. Add ``basket.middleware.BasketMiddleware`` to ``MIDDLEWARE_CLASSES``

3. Add basket to ``urlpatterns`` in your ``urls.py``::

    urlpatterns += patterns('', (r'^basket/', include('basket.urls')))

4. Sync your database::

    ./manage.py syncdb

5. Collect static files::

    ./manage.py collectstatic

Usage
======

Load basket tags: ::

    {% load basket_tags %}
    
Add panel with summary information to template (probably, you want
to include this panel in every page)::

    {% include 'basket/panel.html' %}

In order to basket javascript works, you have to add jQuery and basket.js
to all pages with order buttons::

    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}basket/js/basket.js"></script>

Finally, at the item page ::

    {% add_basket_button object 'button_text' 'added_text' 'already_in_text' 'template_name' %}

Where ``object`` is avaiable to order,
``'button_text'`` is the text printed on the add button,
``'added_text'`` is the text that appears near the add button,
and ``'already_in_text'`` is the text placed above the add button when page loaded.
Unrequired ``'template_name'`` is the path to rendered template.


.. _available-settings:

Available settings
==================

**PRICE_ATTR**

    Default: ``price``
    
    All objects in basket should have this attribute for price calculations.
    Otherwise price will be 0.0

**BASKET_FORM**

    Default: `basket.forms.DefaultOrderForm`
    
    This form class used for order confirmation. By default it has required fields: 
    customer name, customer phone, delivery address, convenient time to call
    and optional textarea for comment.
    All information stored in order comment in admin interface.

**BASKET_OPTIONS_USE_KEEP**

    Default: True
    
    If set to True, user will see checkboxes near all items at basket page.
    If checkbox is unchecked, item will be deleted from basket.


**BASKET_OPTIONS_USE_DELETE**
    
    Default: False
    
    If set to True, user will see delete icons near all items at basket page.
    When user click on icon, item will be deleted from basket by AJAX request
    and basket page will be automatically updated.


**ORDER_STATUSES**
    
    Default: `basket.settings.DEFAULT_ORDER_STATUSES`
    
    An iterable (e.g., a list or tuple) of 2-tuples to use as choices for Order's status field.


**ORDER_EMAIL_SUBJECT**

    Default: `'New order from site'`

    Subject for message emailed to managers after an order confirmed.


Chengelog
==================
    0.6.1 - Use for django >=1.7.
