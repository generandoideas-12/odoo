# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from odoo import http
from odoo.http import request
import base64
from lxml import objectify
from odoo.exceptions import AccessError, MissingError


class SaleOrderAttachments(http.Controller):

    @http.route(
        ['/purchase/order_attachments/<int:order_id>'],
        type='http', auth="user", methods=['POST'], website=True)
    def attach_files(self, order_id, access_token=None, **post):
        
        if 'purchase_order' in request.params:
            if request.params['purchase_order']:
            #     continue
                attached_files = request.httprequest.files.getlist('purchase_order')
                for attachment in attached_files:
                    attached_file = attachment.read()
                    request.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'purchase.order',
                        'res_id': order_id,
                        'type': 'binary',
                        'datas_fname': attachment.filename,
                        'datas': base64.b64encode(attached_file),
                    })          
        
        if 'receipt' in request.params:
            if request.params['receipt']:
            #     continue
                attached_files = request.httprequest.files.getlist('receipt')
                for attachment in attached_files:
                    attached_file = attachment.read()
                    request.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'purchase.order',
                        'res_id': order_id,
                        'type': 'binary',
                        'datas_fname': attachment.filename,
                        'datas': base64.b64encode(attached_file),
                    })

        if 'xml' in request.params:
            if request.params['xml']:
                attached_files = request.httprequest.files.getlist('xml')
                for attachment in attached_files:
                    attached_file = attachment.read()

                    xml = objectify.fromstring(attached_file)
                    total_xml = xml.get('Total', 0)
                    
                    # XML validation
                    # xml = post.get('xml')
                    # att_obj = request.env['ir.attachment']
                    # generated_errors, generated_filename = att_obj.parse_xml(xml,order_id)
                    
                    request.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'purchase.order',
                        'res_id': order_id,
                        'type': 'binary',
                        'datas_fname': attachment.filename,
                        'datas': base64.b64encode(attached_file),
                    })

        if 'pdf' in request.params:
            if request.params['pdf']:
                attached_files = request.httprequest.files.getlist('pdf')
                for attachment in attached_files:
                    attached_file = attachment.read()
                    request.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'purchase.order',
                        'res_id': order_id,
                        'type': 'binary',
                        'datas_fname': attachment.filename,
                        'datas': base64.b64encode(attached_file),
                    })
        
        record_purchase_order = request.env['purchase.order']
        current_purchase_order = record_purchase_order.sudo().search([('id','=',order_id)],limit=1)
                
        return http.request.render('l10n_mx_portal_vendor_bills.attachments_uploaded', {
            'order': current_purchase_order,
            'total_xml': total_xml,
        })
