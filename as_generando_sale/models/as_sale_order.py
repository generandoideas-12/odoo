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


    line_purchases = fields.One2many('as.sale.purchase', 'sale_id', string="Lineas de compras en la Venta",store=True,domain=[('as_product_insig','=',True)])
    line_purchases_picking = fields.One2many('as.sale.purchase', 'sale_id', string="Lineas de compras en la Venta",store=True)
    line_purchases_finanzas = fields.One2many('as.sale.purchase', 'sale_id', string="Lineas de compras en la Venta",store=True,domain=[('as_invoice_id_done','=',True)])
    print_image = fields.Boolean(
        'Print Image', help="""If ticked, you can see the product image in
        report of sale order/quotation""")
    image_sizes = fields.Selection(
        [('image', 'Big sized Image'), ('image_medium', 'Medium Sized Image'),
         ('image_small', 'Small Sized Image')],
        'Image Sizes', default="image_small",
        help="Image size to be displayed in report")
    line_propuesta = fields.One2many('as.propuesta', 'sale_id', string="Lineas de Propueta",store=True)

    
    @api.multi
    def update_create_picking(self):
        for pick in self.picking_ids:
            ultimo= self.line_purchases[int(len(self.line_purchases)-1)].location_app_id.id
            pick.write({
                'location_id': ultimo,
            })
            pick.action_confirm()
            pick.action_assign()
            wiz_id = self.env['stock.immediate.transfer'].with_context(active_ids=pick.ids,active_id=pick.id, default_pick_id=pick.id).create({'pick_id': pick.id})
            wiz_id.process()
            pick.button_validate()



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
                # if len(purchase.picking_ids.ids) > 0:
                insignea = True
                # else:
                #     insignea = False
                vals = {
                    'sale_id':self.id,
                    'purchase_id': purchase.id,
                    'partner_id': purchase.partner_id.id,
                    'state_purchase': purchase.state,
                    'location_app_dest_id': purchase.picking_type_id.default_location_dest_id.id,
                    'as_product_insig': insignea,
                }
                purchase_adeudadas.append(vals)
        return purchase_adeudadas

    @api.multi
    def _action_confirm(self):
        res = super(as_SaleOrder, self)._action_confirm()
        for so in self:
            purchases = so._get_sale_purchase()
            so.line_purchases.create(purchases)
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_small = fields.Binary(
        'Product Image', related='product_id.image_small')

class AsSalesPurchase(models.Model):
    _name = 'as.sale.purchase'


    sale_id = fields.Many2one('sale.order', string="Sale Order")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    partner_id = fields.Many2one('res.partner',string="Proveedor de Producto", store=True)
    partner_app_id = fields.Many2one('res.partner',string="Proveedor de Aplicacion", store=True)
    location_app_id = fields.Many2one('stock.location',string="Ubicacion Destino Producto", store=True, domain=[('usage','=','internal')])
    location_app_dest_id = fields.Many2one('stock.location',string="Ubicacion Origen Producto", store=True)
    state = fields.Selection([('draft', 'Borrador'),('transfer', 'Transferido'),('cancel', 'Cancelado')],string='Estado de Linea a Transferir', readonly=True,default='draft')
    picking_id = fields.Many2one('stock.picking',  string="Movimiento Logistica")
    as_invoice_id = fields.Many2one('account.invoice', string="Factura", copy=False)
    as_invoice_id_done = fields.Boolean( string="producto Insignea", defaul=False)
    as_product_insig = fields.Boolean( string="producto Insignea", defaul=False)
    state_purchase = fields.Selection([('draft', 'RFQ'),('sent', 'RFQ Sent'),('to approve', 'To Approve'),('purchase', 'Purchase Order'),('done', 'Locked'),('cancel', 'Cancelled')], string='Status Compra', readonly=True, default='draft',store=True, related='purchase_id.state')
    #datos de compra
    date_purchase = fields.Datetime(string='Purchase Date',related='purchase_id.date_order')
    total_compra = fields.Monetary(string='Total Compra',related='purchase_id.amount_total')
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Orden de Entrega',related='purchase_id.picking_ids')
    #campos d efactura
    date_invoice = fields.Date(string='Invoice Date',related='as_invoice_id.date_invoice')
    number = fields.Char(string='Numero',related='as_invoice_id.name')
    currency_id = fields.Many2one('res.currency', string='Currency',related='as_invoice_id.currency_id')
    ref = fields.Char(string='Ref. de pago',related='as_invoice_id.reference')
    date_vence = fields.Date(string='Fecha de Vencimiento',related='as_invoice_id.date_due')
    impuesto = fields.Monetary(string='Impuesto de Incluido',related='as_invoice_id.amount_tax')
    impuesto_no = fields.Monetary(string='Impuesto no Incluido',related='as_invoice_id.amount_untaxed')
    amount_total = fields.Monetary(string='Impuesto no Incluido',related='as_invoice_id.amount_total')
    residual = fields.Monetary(string='A pagar',related='as_invoice_id.residual')
    state_invoice = fields.Selection([('draft', 'Draft'),('open', 'Open'),('paid', 'Paid'),('cancel', 'Cancelled')], string='Invoice Status',related='as_invoice_id.state')

    def _compute_picking(self):
        for lines in self:
            for order in lines.purchase_id:
                pickings = self.env['stock.picking']
                for line in order.order_line:
                    moves = line.move_ids | line.move_ids.mapped('returned_move_ids')
                    pickings |= moves.mapped('picking_id')
                order.picking_ids = pickings
                order.picking_count = len(pickings)
        
    @api.multi
    def action_create_picking(self):
        picking_type = self.env['stock.picking.type'].sudo().search([('default_location_dest_id', '=', self.location_app_id.id)], limit=1)
        location_src_id = self.location_app_dest_id
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
        # sp2.action_confirm()as_product_insig
        # wiz_id = self.env['stock.immediate.transfer'].with_context(active_ids=sp2.ids, active_id=sp2.id, default_pick_id=sp2.id).create({'pick_id': sp2.id})
        # wiz_id.process()
        # sp2.button_validate()
        self.write({
            'state': 'transfer',
            'picking_id': sp2.id,
        })
        #crear movimiento 
        vals = {
                'sale_id':self.sale_id.id,
                'purchase_id': self.purchase_id.id,
                'partner_id': self.partner_app_id.id,
                'state_purchase': self.purchase_id.state,
                'location_app_dest_id': sp2.location_dest_id.id,
                'as_product_insig': True,
            }
        line  = self.create(vals)
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
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_app_id.id,
            'account_id': self.partner_app_id.property_account_payable_id.id,
        })
        for line in self.sale_id.order_line:
            if line.product_id.type == 'product':
                self.env['account.invoice.line'].create({
                    'invoice_id': invoice.id,
                    'account_id': line.product_id.property_account_income_id.id,
                    'name': line.product_id.product_tmpl_id.name,
                    'quantity' : line.product_uom_qty,
                    'price_unit' : line.price_unit,
                })
        invoice.action_invoice_open()
        self.as_invoice_id = invoice.id
        self.as_invoice_id_done = True
        return True

class AsSalesPurchase(models.Model):
    _name = 'as.propuesta'

    sale_id = fields.Many2one('sale.order', string="Sale Order")
    propuesta = fields.Binary(string ='Propuesta')
    state = fields.Selection([('aprobado', 'Aprobado'),('re-trabajar', 'Re-Trabajar'),('no-aplica', 'No Aplica')], string='Status')
    observaciones = fields.Char(string ='Observaciones')