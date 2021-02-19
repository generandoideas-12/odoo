# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "Website Menu and Page Security",
	"version" : "12.0.0.0",
	"category" : "Website",
	'summary': 'Website hide any menu website hide sub-menu website hide pages for user website page security website menu security shop page security shop menu security hide page on website hide menu on website invisible menu website invisible menu hide menu on shop',
	"description": """
		This module helps hide any menu item for a particular type of user , particular group , particular user
		It also restrict users , users having specific group , user of particular type to see website pages, 
		also you can restrict user to access any page when he/she is not logged-in
		
	""",
	"author": "BrowseInfo",
	"website" : "https://www.browseinfo.in",
	"price": 8,
	"currency": 'EUR',
	"depends" : ['website'],
	"data": [
		'security/ir.model.access.csv',
		'views/page_security.xml',
		'views/user_error_template.xml',
		'views/hide_menu_view.xml',
		'data/demo.xml',
		'views/website_templates.xml',
	],
	'qweb': [
	],
	"auto_install": False,
	"installable": True,
	"live_test_url":'https://youtu.be/YvpijS0c8Dc',
	"images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
