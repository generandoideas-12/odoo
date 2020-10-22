from odoo import api, fields, models


class purchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_count = fields.Integer(
        compute='_compute_purchase_count')

    @api.multi
    def _compute_purchase_count(self):
        purchase_order_model = self.env['purchase.order']
        for mo in self:
            domain = [('origin', 'ilike', mo.name)]
            mo.purchase_count = purchase_order_model.search_count(domain)

    @api.multi
    def action_view_purchase(self):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        productions = self.env['mrp.production'].search(
            [('sale_order_id', 'in', self.ids)])
        if len(productions) > 1:
            action['domain'] = [('id', 'in', productions.ids)]
        else:
            action['views'] = [
                (self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            action['res_id'] = productions.id
        return action