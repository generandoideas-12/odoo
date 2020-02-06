# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PosSalesOrder(models.Model):
    _name = "pos.sales.order"
    _description = "Create a sale order through point of sale for home delivery"

    @api.model
    def create_pos_sale_order(self, ui_order, note, cashier, client_fields, exp_date):
        wk_exp_date = False
        if exp_date:
            wk_exp_date = (datetime.strptime(exp_date, '%m/%d/%Y')).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        vals = {'partner_id':   ui_order['partner_id'] or False,
                'pos_notes': note,
                'user_id': cashier,
                'client_order_ref': 'Point of sale',
                'validity_date': wk_exp_date,
                }
        if client_fields:
            partner_id = self.env['res.partner'].create(client_fields)
            vals['partner_shipping_id'] = partner_id.id
        order_id = self.env['sale.order'].create(vals)
        for ui_order_line in ui_order['lines']:
            product = self.env['product.product'].browse(int(ui_order_line[2]['product_id']))
            values = {
                'order_id': order_id.id,
                'product_id': ui_order_line[2]['product_id'],
                'product_uom_qty': ui_order_line[2]['qty'],
                'price_unit': ui_order_line[2]['price_unit'],
                'name': product.name,
                'product_uom': product.uom_id.id,
                'discount': ui_order_line[2]['discount'],
            }
            if product.description_sale:
                values['name'] += '\n' + product.description_sale
            order_line = self.env['sale.order.line'].create(values)
            order_line._compute_tax_id()
        return {'name': order_id.name, 'id': order_id.id}

    @api.model
    def wk_print_quotation_report(self):
        report_ids = self.env['ir.actions.report.xml'].search([('model', '=', 'sale.order'), ('report_name', '=', 'sale.report_saleorder')])
        return report_ids and report_ids[0].id or False

    @api.model
    def send_email(self, quotation_id):
        if quotation_id:
            res_id = int(quotation_id)
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
            if template_id:
                template_obj = self.env['mail.template'].browse(template_id)
                mail_confirmed = template_obj.send_mail(res_id, True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_notes = fields.Text(string='POS Notes')


class PosConfig(models.Model):
    _inherit = 'pos.config'

    extra_price_product_id = fields.Many2one('product.product', string='Extra Price Product', domain=[(
        'type', '=', 'service'), ('available_in_pos', '=', True)], help='The product used to manage extra price')
