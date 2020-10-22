# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta

class as_HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # partner_name = fields.Char(string='Customer Name',default=_get_default_partner)

    # @api.model
    # def _get_default_partner(self):
    #     ctx = self._context
    #     if ctx.get('active_model') == 'sale.order':
    #         return self.env['sale.order'].browse(ctx.get('active_ids')[0]).partner_id.id
        