from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_count = fields.Integer(
        compute='_compute_production_count')

    @api.multi
    def _compute_production_count(self):
        mrp_production_model = self.env['mrp.production']
        for sale in self:
            domain = [('sale_order_id', '=', sale.id)]
            sale.production_count = mrp_production_model.search_count(domain)

    @api.multi
    def action_view_production(self):
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

class SaleOrderline(models.Model):
    _inherit = 'sale.order.line'
    
    mo_id = fields.Many2one(
        'mrp.production', string='MO', store=True)    
    
    # @api.depends('state')
    # def _get_mo(self):
    #     for line in self:
    #     #TODO: this is not the best way to get sale_line_id, find better way.
    #         # we should write the sale_line_id on MO creation - see mrp/models/procurement.py,make_mo()
    #         # the proc that creates the MO don't have the sale_line_id, this is the raw mat. proc order,
    #         # we should find link between raw proc order and finished product proc order.
    #         if line.state == 'sale':
    #             mo = self.env['mrp.production'].sudo().search([
    #             ('sale_order_id', '=', line.order_id.id)], limit=1)
                
    #             line.mo_id = mo.id