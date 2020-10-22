from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one(
        comodel_name='sale.order', string='Source Sale Order')

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
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        purchases = self.env['purchase.order'].search(
            [('origin', 'ilike', self.name)])
        if len(purchases) > 1:
            action['domain'] = [('id', 'in', purchases.ids)]
        else:
            action['views'] = [
                (self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = purchases.id
        return action

    @api.model
    def create(self, values):
        if 'origin' in values:
            # Checking first if this comes from a 'sale.order'
            sale_id = self.env['sale.order'].search([
                ('name', '=', values['origin'])
            ], limit=1)
            if sale_id:
                values['sale_order_id'] = sale_id.id
                if sale_id.client_order_ref:
                    values['origin'] = sale_id.client_order_ref
            else:
                # Checking if this production comes from a route
                production_id = self.env['mrp.production'].search([
                    ('name', '=', values['origin'])
                ])
                # If so, use the 'sale_order_id' from the parent production
                values['sale_order_id'] = production_id.sale_order_id.id
        
        return super(MrpProduction, self).create(values)

    sale_line_id = fields.Many2one(
        'sale.order.line', string='Sale Product Line', readonly=True, store=True,
        compute='_get_sale_line')

    # sale_id = fields.Many2one('sale.order', string='Sale order', readonly=True,
    #     store=True, related='sale_line_id.order_id')

    # partner_id = fields.Many2one(related='sale_id.partner_id', readonly=True,
    #     string='Customer', store=True)
    
    @api.depends('origin')
    def _get_sale_line(self):
        for prd in self:
            if prd.product_id.id:
                sol_product_id = self.env['sale.order.line'].sudo().search([
                ('product_id', '=', prd.product_id.id),
                ('order_id','=',prd.sale_order_id.id),
                ('product_uom_qty','=',prd.product_uom_qty)], limit=1)
                
                    
                _logger.debug('\n\n sol_product_id: %d ', sol_product_id.id)
                
                # actualizar en el sol el id del mo
                if sol_product_id.id:
                    prd.sale_line_id = sol_product_id.id
                    sql_query = 'update sale_order_line set mo_id = ' + str(prd.id) + ' where id = ' + str(prd.sale_line_id.id)
                    self.env.cr.execute(sql_query)