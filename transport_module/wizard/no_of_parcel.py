# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 BrowseInfo (<http://Browseinfo.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api

class parcel_entry_wizard(models.TransientModel):
    
    _name = 'parcel.entry.wizard'
    
    no_of_parcel = fields.Integer('No Of Parcel')
                
    @api.multi	
    def	add_no_of_parcels(self):
    	if self._context:
    		if self._context.get('active_model') == 'stock.picking':
    			active_id  = self._context.get('active_id')
    			stock_picking_object = self.env['stock.picking'] 
    			current_record = stock_picking_object.browse(active_id)
    			current_record.no_of_parcels = self.no_of_parcel
    			transport_entry_record = self.env['transport.entry'].search([('picking_id','=',active_id)])
    			if transport_entry_record:
    				transport_entry_record.write({'no_of_parcels':self.no_of_parcel})
    			current_record.parcel_entry_done = True
 


 												
