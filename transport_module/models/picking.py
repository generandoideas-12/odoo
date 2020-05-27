# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class stock_picking(models.Model):
    
    _inherit  = 'stock.picking'

    @api.multi
    def write(self, vals):
        if vals.get('no_of_parcels') or vals.get('lr_number'):
           #searching transport entry
           search_transport_entry_ids = self.env['transport.entry'].search([('picking_id','=', self.id)])
           if search_transport_entry_ids:
               transport_entry = search_transport_entry_ids[0]
               if vals.get('no_of_parcels'):
                   transport_entry.no_of_parcels = vals.get('no_of_parcels')
                   if vals.get('lr_number'):
                       transport_entry.lr_number = vals.get('lr_number')
        return super(stock_picking, self).write(vals)

    @api.model
    def create(self, val):

        if val.get('origin'):
            sale_order_object = self.env['sale.order']
            sale_order_record = sale_order_object.search([('name', '=',val.get('origin') )])
            if sale_order_record:
                sale_order_record = sale_order_record[0]
                if sale_order_record.transport_id:
                    val.update({'transport_id': sale_order_record.transport_id.id })
                    res= super(stock_picking, self).create(val)                                 
                else:
                    res= super(stock_picking, self).create(val) 
            else:
                res= super(stock_picking, self).create(val)

        else :    
            res= super(stock_picking, self).create(val)                                                          
        return res

    @api.multi
    def action_assign(self):
        for a in self:
            entry = self.env['transport.entry'].search([('picking_id', '=', a.id)])
            if not entry: 
                self.env['transport.entry'].create({
                    'date': date.today(),
                    'active' : True,
                    'picking_id':a.id,
                    'vehicle_id' :a.transport_id.vehicle_id.id,
                    'lr_number':a.lr_number,
                    'customer_id':a.partner_id.id,
                    'contact_person':a.transport_id.contact_name,
                    'no_of_parcels':a.no_of_parcels,
                    'active': True,
                    'transport_id':a.transport_id.id,
                })
        return super(stock_picking, self).action_assign()
                                                    
