# -*- coding: utf-8 -*-

import time

import odoo
from odoo import api, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import psycopg2

import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_compare
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)
#clase heredada de purchase order para agregar funciones de creacion de facturas y campos adicionales
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        as_sales_create = self.env['as.sale.purchase']
        as_sales_purchase = self.env['as.sale.purchase'].sudo().search([('purchase_id', '=', self.id)],limit=1)
        for pick in self.picking_ids:
            vals = {
                    'sale_id':as_sales_purchase.sale_id.id,
                    'purchase_id': self.id,
                    'partner_id': self.partner_id.id,
                    'partner_app_id': self.partner_id.id,
                    'state_purchase': self.state,
                    'location_app_dest_id': pick.location_id.id, #origen
                    'location_app_id':  pick.location_dest_id.id, #destino
                    'state':  'transfer', #destino
                    'picking_id':  pick.id, #picking
                    'as_product_almacenable':  True, #picking
            }
            line  = as_sales_create.create(vals)
        return res