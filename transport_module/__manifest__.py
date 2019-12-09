# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Freight Transport Management and Delivery Routes in Odoo',
    'version': '12.0.0.4',
    'category': 'Sales',
    'summary': 'Transport management system integrated with sales and delivery order',
    'description'	: """
        Features of this Module includes::
        odoo transport module
        odoo Managing transport details enter transport details with sales order linked transport details with the picking Transport management with delivery order
        odoo Transport Management and Delivery Routes Picking Transport Details
        odoo Transport Route Locations Freight Management Transportation logistics management Route optimization
        odoo Transport Routes Delivery Routes management logestic transport management Transporters Details
        odoo Vehicles Transport Vehicles Freight Transport module
        odoo Freight Management Freight transport
        odoo Transportation management systems 
        odoo TMS Transportation Management and Logistics System Freight Management Services
        odoo freight transportation pdf freight transportation Transport Management System
        odoo Transporters Vehicles Odoo Transport Management Delivery Routes System
        Freight Transport Management and Delivery Routes System

 Gestión de detalles de transporte, introducción de detalles de transporte con pedido de cliente, detalles de transporte vinculados con el picking, gestión de transporte con pedido de entrega,
         Gestión del transporte y rutas de entrega
         Recoger detalles de transporte
         Ubicaciones de rutas de transporte
         Rutas de transporte
         Detalles de los transportadores
         Transporte de vehículos

-Gérer les détails de transport, entrer les détails de transport avec la commande client, les détails de transport liés à la cueillette, la gestion du transport avec ordre de livraison,
         Gestion du transport et itinéraires de livraison
         Détails de transport de prélèvement
         Emplacements des itinéraires de transport
         Routes de transport
         Détails des transporteurs
         Transport de véhicules
    """,
    'author': 'BrowseInfo',
    'price': 45.00,
    'currency': "EUR",
    'website': 'http://www.browseinfo.in',
        'live_test_url':'https://www.youtube.com/watch?v=czYpBO31y3Y',
    'depends': ['base', 'sale', 'sale_management', 'stock', 'sale_stock' , 'account', 'fleet'],

    'data': [

             "security/ir.model.access.csv",
             'views/view_of_no_of_parcel_wizard.xml',
             'report/inherited_delivery_slip_report.xml',
             'views/transport.xml',
             'views/transport_entry_report.xml',
             'views/transport_report.xml',
            'report/transport_report_menu.xml',
            'report/transport_document.xml'
            ],
    'demo': [],
    'test': [
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


