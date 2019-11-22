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

class as_purchase_OrderLine(models.Model):
    _inherit = "purchase.order"
    
    @api.depends('order_line.price_total')
    def _amount_all_integer(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed_integer': order.currency_id.round(amount_untaxed),
                'amount_tax_integer': order.currency_id.round(amount_tax),
                'amount_total_integer': amount_untaxed + amount_tax,
            })

    amount_untaxed_integer = fields.Integer(string='Sin Impuestos', store=True, readonly=True, compute='_amount_all_integer')
    amount_tax_integer = fields.Integer(string='Impuestos', store=True, readonly=True, compute='_amount_all_integer')
    amount_total_integer = fields.Integer(string='Total', store=True, readonly=True, compute='_amount_all_integer')

class as_purchase_OrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount_integer(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_subtotal_integer': taxes['total_excluded'],
            })
                
    price_subtotal_integer = fields.Integer(compute='_compute_amount_integer', string='Subtotal', store=True)