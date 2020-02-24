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
        as_sales_purchase = self.env['as.sale.purchase'].sudo().search([('purchase_id', '=', self.id)])
        for purchase_sale in as_sales_purchase:
            if len(self.picking_ids.ids) > 0:
                insignea = True
            else:
                insignea = False
            as_sales_purchase.write({
                'location_app_dest_id': self.picking_type_id.default_location_dest_id.id,
                'as_product_insig': insignea,
            })
        return res