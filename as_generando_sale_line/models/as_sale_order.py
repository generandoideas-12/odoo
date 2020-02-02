# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from werkzeug.urls import url_encode

import logging
logger = logging.getLogger(__name__)

class as_SaleOrder(models.Model):
    _inherit = "sale.order"


      

class as_SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.model
    def compute_get_default_partner(self):
        
        ctx = self._context
        cliente = self.env['res.partner'].search([('id','=',ctx.get('partner_id'))],limit=1)
            
        return cliente.name or "Guarde la Venta Primero"
        #     return self.env['sale.order'].browse(ctx.get('active_ids')[0]).partner_id.id

    image_small = fields.Binary('Product Image',related='product_id.image_small')
    
    as_customer_name = fields.Char('as_customer_name',default=compute_get_default_partner)
    
