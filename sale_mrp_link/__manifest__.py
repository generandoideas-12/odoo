# -*- coding: utf-8 -*-

{
    'name': 'Ahorasoft Sale MRP Link',
    'summary': 'Show manufacturing orders generated from sales order',
    'version': '1.1',
    # 'development_status': 'Production/Stable',
    'category': 'Sales Management',
    'website': 'http://ahorasoft.com',
    'author': 'Ahorasoft.com',
    # 'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'sale_mrp',
    ],
    'data': [
        'views/mrp_production.xml',
        'views/sale_order.xml',
    ],
}
