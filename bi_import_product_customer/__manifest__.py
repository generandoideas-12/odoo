# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Products and Partners from Excel or CSV File',
    'version': '12.0.0.6',
    'sequence': 11,
    'category' : 'Extra Tools',
    "price": 25,
    "currency": 'EUR',
    'summary': 'This apps helps easy to import your product and customer from CSV or Excel file.',
    'description': """
	BrowseInfo developed a new odoo/OpenERP module apps 
	This module use for following easy import.
	-Import product from CSV and Excel file.
	-Import product from Excel and CSV file.
	-Import variant from CSV and Excel file.
	-Import variant from Excel and CSV file.
	-Import product variant from CSV and Excel file.
	-Import product variant from Excel and CSV file.

	-Import item from CSV and Excel file.
	-Import item from Excel and CSV file.

	-Import partner from CSV and Excel file.
	-Import vendor from csv and excel file
	-Import partner from Excel and CSV file.
	-Import contact from CSV and Excel file.
	-Import contact from Excel and CSV file.
	-Import Customer from CSV and Excel file.
	-Import customer from Excel and CSV file.
	-Import Supplier from CSV and Excel file.
	-Import supplier from Excel and CSV file.



	-Update product from CSV and Excel file.
	-Update product from Excel and CSV file.
	-Update variant from CSV and Excel file.
	-Update variant from Excel and CSV file.
	-Update product variant from CSV and Excel file.
	-Update product variant from Excel and CSV file.

	-Update item from CSV and Excel file.
	-Update item from Excel and CSV file.

	-Update partner from CSV and Excel file.
	-Update vendor from csv and excel file
	-Update partner from Excel and CSV file.
	-Update contact from CSV and Excel file.
	-Update contact from Excel and CSV file.
	-Update Customer from CSV and Excel file.
	-Update customer from Excel and CSV file.
	-Update Supplier from CSV and Excel file.
	-Update supplier from Excel and CSV file.

	item import from csv, product import from csv, catelog import from csv, contact import from csv, partner import from csv, customer import from csv, supplier import from csv,variant import from csv, product variant import from csv, vendor import from csv

	item import from excel, product import from excel, catelog import from excel, contact import from excel, partner import from excel, customer import from excel, supplier import from excel,variant import from excel, product variant import from excel, vendor import from excel

	item import csv, product import csv, catelog import csv, contact import csv, partner import csv, customer import csv, supplier import csv,variant import csv, product variant import csv, vendor import csv

	item import excel, product import excel, catelog import excel, contact import excel, partner import excel, customer import excel, supplier import excel,variant import excel, product variant import excel, vendor import excel

	-Import product from CSV, Import customer from CSV, Product Import,Customer import, Odoo CSV bridge,Import CSV brige on Odoo
    """,
    'author': 'BrowseInfo',
    'website': '',
    'depends': ['base','sale','sale_management','stock','purchase'],
    'data': [
    	"security/import_security.xml",
         "views/product_view.xml",    
	     "views/partner.xml",
	     "views/product_variant.xml"

             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/QiBI2C1k0qY',
    "images":["static/description/Banner.png"],
}
