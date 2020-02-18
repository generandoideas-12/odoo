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


    line_purchases = fields.One2many('as.sale.purchase', 'sale_id', string="Lineas de compras en la Venta",store=True)
    line_purchases_picking = fields.One2many('as.sale.purchase', 'sale_id', string="Lineas de compras en la Venta",store=True,domain=[('state','=','transfer')])
    line_purchases_finanzas = fields.One2many('as.sale.purchase', 'sale_id', string="Lineas de compras en la Venta",store=True,domain=[('as_invoice_id','!=','')])
    print_image = fields.Boolean(
        'Print Image', help="""If ticked, you can see the product image in
        report of sale order/quotation""")
    image_sizes = fields.Selection(
        [('image', 'Big sized Image'), ('image_medium', 'Medium Sized Image'),
         ('image_small', 'Small Sized Image')],
        'Image Sizes', default="image_small",
        help="Image size to be displayed in report")
    
    @api.multi
    def create_picking(self):
        pass

    @api.multi
    def line_product_edit(self):
        posiciones_insigneas = []
        insignea=0
        bandera = False
        for line in self.order_line:
            if line.product_id.product_tmpl_id.x_studio_producto_insignia == True:
                line_venta={}
                if insignea == 0 and bandera== False:
                    bandera=True
                    insignea=0
                elif bandera==True:
                    insignea+=1
                line_venta= {
                        'image': line.product_id.image,
                        'price_total': line.price_total,
                        'display_type': line.display_type,
                        'display_type': line.display_type,
                        'display_type': line.display_type,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.name,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'tax_id': line.tax_id,
                        'price_subtotal': line.price_subtotal,
                        'price_total': line.price_total,
                        'display_type ': line.display_type,
                        'name': line.name,
                        'display_type ': line.display_type ,
                        'name': line.name,
                        'material': line.product_id.product_tmpl_id.x_studio_material,
                        'medidas': line.product_id.product_tmpl_id.x_studio_medidas,
                        'aplicacion': '',
                    }
                posiciones_insigneas.append(line_venta)
            else:
                if line.product_id.product_tmpl_id.x_studio_sumar_descripcin_1 == True:
                    posiciones_insigneas[insignea]['name']= posiciones_insigneas[insignea]['name']+'/'+line.name
                    posiciones_insigneas[insignea]['price_subtotal']+=line.price_subtotal
                elif line.product_id.product_tmpl_id.x_studio_sumar_descripcin_1 == False and line.product_id.product_tmpl_id.x_studio_aplicacin_1 == False:
                    posiciones_insigneas[insignea]['price_subtotal']+=+line.price_subtotal
                if line.product_id.product_tmpl_id.x_studio_aplicacin_1 == True:
                    posiciones_insigneas[insignea]['aplicaciobol']= True
                    posiciones_insigneas[insignea]['aplicacion']= line.name
                    posiciones_insigneas[insignea]['price_subtotal']+=line.price_subtotal
                
        return posiciones_insigneas

    @api.multi
    def _action_confirm(self):
        res = super(as_SaleOrder, self)._action_confirm()
        for so in self:
            purchases = so._get_sale_purchase()
            so.line_purchases.create(purchases)
        return res

    @api.multi
    def _get_sale_purchase(self):
        purchase_adeudadas = []
        if self.name:
            line_purchase = self.env['as.sale.purchase']
            resultado_consulta = []
            sql = ''
            partner = 0
            if self.partner_id.id:
                partner = self.partner_id.id
            where = " where po.origin ilike "+"'%"+self.name+"%'"
            consulta = "SELECT po.id FROM purchase_order AS po"+ where +" ORDER BY po.date_order"
            self.env.cr.execute(consulta)
            for i in self.env.cr.fetchall():
                resultado_consulta.append(i[0])
            purchases = self.env['purchase.order'].sudo().search([('id', 'in', resultado_consulta)])
            for purchase in purchases:
                vals = {
                    'sale_id':self.id,
                    'purchase_id': purchase.id,
                    'partner_id': purchase.partner_id.id,
                }
                purchase_adeudadas.append(vals)
        return purchase_adeudadas

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_small = fields.Binary(
        'Product Image', related='product_id.image_small')

    @api.multi
    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

        #     try:
        #         self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
        #     except UserError as error:
        #         errors.append(error.name)
        # if errors:
        #     raise UserError('\n'.join(errors))
        return True

class AsSalesPurchase(models.Model):
    _name = 'as.sale.purchase'

    sale_id = fields.Many2one('sale.order', string="Sale Order")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    partner_id = fields.Many2one('res.partner',string="Proveedor de Producto", store=True)
    partner_app_id = fields.Many2one('res.partner',string="Proveedor de Aplicacion", store=True,required=True)
    location_app_id = fields.Many2one('stock.location',string="Ubicacion Producto", store=True,required=True)
    state = fields.Selection([('draft', 'Confirmado'),('transfer', 'Transferido'),('cancel', 'Cancelado')],string='Status', readonly=True,default='draft')
    picking_id = fields.Many2one('stock.picking',  string="Movimiento Logistica")
    as_invoice_id = fields.Many2one('account.invoice', string="Factura", copy=False)

    @api.multi
    def action_create_picking(self):
        picking_type = self.env['stock.picking.type'].sudo().search([('default_location_dest_id', '=', self.location_app_id.id)], limit=1)
        location_src_id = self.env['stock.location'].search([('usage','=','supplier')],limit=1)
        vals = {
            'name' : picking_type.sequence_id.next_by_id() if picking_type else '/',
            'state' : 'draft',
            'location_id' : location_src_id.id,
            'location_dest_id' : self.location_app_id.id,
            'picking_type_id'  : picking_type.id,
            'date' : self.purchase_id.date_order,
            'origin' : str(self.purchase_id.name)+', '+str(self.sale_id.name),
            'partner_id': self.partner_app_id.id,
        }
        sp2  = self.env['stock.picking'].create(vals)
        for line in self.sale_id.order_line:
            if line.product_id.type == 'product':
                vals = {
                    'name' :  line.product_id.name,
                    'picking_id' : int(sp2.id),
                    'location_id' : sp2.location_id.id,
                    'location_dest_id' : sp2.location_dest_id.id,
                    'product_id' : line.product_id.id,
                    'price_unit' : line.price_unit,
                    'product_uom' : line.product_uom.id,
                    'product_uom_qty' : line.product_uom_qty,
                    'sale_line_id' : line.id,
                }
                line_id = self.env['stock.move'].create(vals)
        # sp2.action_confirm()
        # wiz_id = self.env['stock.immediate.transfer'].with_context(active_ids=sp2.ids, active_id=sp2.id, default_pick_id=sp2.id).create({'pick_id': sp2.id})
        # wiz_id.process()
        # sp2.button_validate()
        self.write({
            'state': 'transfer',
            'picking_id': sp2.id,
        })
        return True

    @api.multi
    def action_anular_picking(self):
        purchase_adeudadas = []
        self.picking_id.action_cancel()
        line_purchase = self.env['as.sale.purchase']
        vals = {
            'sale_id':self.sale_id.id,
            'purchase_id': self.purchase_id.id,
            'partner_id': self.purchase_id.partner_id.id,
        }
        purchase_adeudadas.append(vals)
        line_purchase.create(purchase_adeudadas)
        self.write({
            'state': 'cancel',
        })
        return True

    @api.multi
    def action_invoice_supplier(self):
        action = self.env.ref('as_generando_sale.action_open_window_edit')
        result = action.read()[0]
        result['target'] = 'new'
        result['flags'] = {'form': {'action_buttons': True}}
        result['res_id'] = self.id
        return result

    #crear factura de importacion
    def action_create_invoice(self):  
        #lineas de la factura
        lines_invoice = []
        for line in self.sale_id.order_line:
            if line.product_id.type == 'product':
                lines_invoice.append({
                    'name' : line.name,
                    'product_id' : line.product_id.id,
                    'quantity' : line.product_uom_qty,
                    'price_unit' : line.price_unit,
                    })      
        values = {
            'partner_id': self.partner_app_id.id,
            'account_id' : self.partner_app_id.property_account_payable_id.id,
            'date_invoice' : str(self.sale_id.date_order),
            'reference' : str(self.sale_id.name)+', '+str(self.purchase_id.name),
            'state' : 'draft',
            'origin' : str(self.sale_id.name)+', '+str(self.purchase_id.name),
            'invoice_line_ids': lines_invoice,
        }
        factura_obj = self.env['account.invoice'].with_context(
            type='in_invoice',state='draft').create(values)
        factura_obj.action_invoice_open()
        self.as_invoice_id = factura_obj.id
        return True