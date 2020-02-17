# -*- coding: utf-8 -*-

{
    'name': 'Website Hide Price for Not Logged In User',
    'version': '12.0.1.0.0',
    'category': 'Website',
    'summary': 'Hide Price for Not Logged In User in Website Sale',
    'description': """
        This module allow to hide price for not logged in user in website sale
    """,
    'sequence': 1,
    'author': 'Futurelens',
    'website': 'http://thefuturelens.com',
    'depends': ['website_sale'],
    'data': [
        'views/product_price_template.xml'
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/banner_website_hide_price.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'price': 5,
    'currency': 'EUR',
}
