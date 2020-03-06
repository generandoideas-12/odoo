{
    "name": "Generando Ventas",
    "summary": "Nucleo para Ventas",
    "category": "crm",
    "images": [],
    "version": "1.1.3",
    "application": True,
    "author": "Ahorasoft",
    "support": "soporte@ahorasoft.com",
    "website": "http://www.ahorasoft.com",
    "depends": [
        "crm",
        "sale",
        'base',
        'sale_management',
        'account',
        'helpdesk',
        'purchase',
    ],
    'data': [
        'report/as_report_sale_order.xml',
        'report/as_report_invoice.xml',
        'views/as_sale_order.xml',
        'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,

}