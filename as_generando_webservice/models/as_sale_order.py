# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.exceptions import UserError
from . import as_amount_to_text_es
from odoo.tools import float_is_zero, float_compare
from odoo.tools.float_utils import float_round, float_is_zero
from datetime import datetime
from dateutil import relativedelta

from werkzeug.urls import url_encode

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    as_nit = fields.Char(string="NIT")
    as_razon_social = fields.Char(string="Razon Social") 
    as_forma_pago_id = fields.Many2one('as.metodo.pago.ventas', 'Forma de Pago')
    
    #numeracion para ventas
    @api.multi
    def _numeracion_interna(self):
        editable = self.env['ir.config_parameter'].sudo().get_param('sale_config_settings.as_numeracion_interna_editable')
        return editable

    @api.multi
    def as_mostrar_imagen(self):
        editable = self.env['ir.config_parameter'].sudo().get_param('sale_config_settings.as_mostrar_imagen_descripcion')
        return editable

    def logo(self):
        as_logo_cotizaciones_notas = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_logo_cotizaciones_notas'))
        return as_logo_cotizaciones_notas or False
    
    @api.multi
    def incluir_numeracion_interna(self):
        if self.env['ir.config_parameter'].sudo().get_param('sale_config_settings.as_incluir_numeracion_interna'):
            return self.as_numeracion_interna
        else:
            return ''

    @api.multi
    def _pricelist_editable(self):
        if not self.env.user._is_admin():
            return True
        else:
            return ''

    #cancelar ventas
    @api.multi
    def action_cancel(self):
        for sol in self:
            invoices = self.env['account.invoice'].sudo().search([('origin','=',sol.name),('as_status','=','valida')])
            if invoices:
                raise UserError(_("El pedido de venta tiene una o mas facturas VALIDAS.\n Por favor ANULAR la(s) factura(s) si necesita realizar cambios."))
            else:
                result = super(SaleOrder, self).action_cancel()
        return result
    #confirma venta heredada

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder,self).action_confirm()
        for line in self.order_line:
            sale_price= self.env['product.pricelist.item'].search([('product_tmpl_id','=',line.product_id.product_tmpl_id.id),('pricelist_id','=',self.pricelist_id.id)],limit=1)
            if sale_price:
                cantidad = line.product_uom_qty 
                if line.product_id.uom_id != line.product_uom:
                    cantidad = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                if cantidad < sale_price.min_quantity:
                    raise UserError(_("la cantidad de los productos a vender no puede ser menor a la cantidad minima registrada."))
        modulo = self.env['ir.module.module'].sudo().search([("name","=","as_stock_product"),("state","=","installed")])
        if modulo:
            for picking in self.picking_ids:
                for move in picking.move_lines:
                    quant = self.env['stock.quant'].sudo().search([('product_id', '=', move.product_id.id),('location_id', '=', move.location_id.id)], limit=1)
                    move.price_unit = quant.value_unit
        if not self.as_numeracion_interna_editable:
            if not self.as_numeracion_interna:
                self.as_numeracion_interna = self.env['ir.sequence'].next_by_code('sale.order.interna') or 'New'
        #validez de los precios en el presupuesto
        if self.state == 'sale':
            fecha_validez = str(self.validity_date)
            fecha_actual = str(datetime.now().strftime('%Y-%m-%d'))
            if fecha_validez <= fecha_actual:
                for line in self.order_line:
                    if line.order_id.pricelist_id:
                        price =  line.order_id.pricelist_id.get_product_price(line.product_id, line.product_uom_qty or 1.0, line.order_id.partner_id)
                        line.update({
                            'price_unit': price
                        })

        return result
    
    @api.one
    @api.depends('name')
    def _obtener_dato_factura(self):
        self.as_dato_factura = ''
        dato = self.env['account.invoice'].sudo().search([('origin', '=', self.name)], limit=1)
        #_logger.debug("\n\n\n\nDATO FACTURA... %s\n\n\n\n",dato)
        if dato:
            self.as_dato_factura = dato.invoice_number
    
    as_dato_factura = fields.Char(string="Nro Factura", compute='_obtener_dato_factura')
        
    as_numeracion_interna_editable = fields.Boolean(string='Numeracion interna editable', help='Verifica si la numeracion interna es editable o no', default=_numeracion_interna)
    as_pricelist_editable = fields.Boolean(string='Pricelist editable', default=_pricelist_editable)
    as_numeracion_interna = fields.Char('Numeracion Interna', help=u'Numeración interna de ventas confirmadas.', copy=False)

    #trae el nit y razon social del cliente
    @api.onchange('partner_id')
    def onchanges_partner(self):
        self.as_nit = self.partner_id.vat
        self.as_razon_social = self.partner_id.business_name
    
    #funcion heredada para agregar campos adicionales a la factura
    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        fecha = str(self.confirmation_date)
        if self.as_fecha_caducidad:
            fecha = str(datetime.strptime(str(self.as_fecha_caducidad), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'as_nit': self.as_nit,
            'as_razon_social': self.as_razon_social,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'date_due': fecha,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
        }
        return invoice_vals
        
    @api.one
    @api.depends('partner_id','payment_term_id')
    def _fecha_caducidad(self):
        fecha = None
        if self.payment_term_id and self.payment_term_id.line_ids[0].days != 0:
            d = timedelta(days=self.payment_term_id.line_ids[0].days)
            fecha_venta = datetime.strptime(str(self.date_order) ,'%Y-%m-%d %H:%M:%S')
            fecha = d + fecha_venta
        self.as_fecha_caducidad = fecha
        
    as_credit_limit_days = fields.Integer(string="Dias de credito",
        readonly=True,
        states={'draft': [('readonly', False)],'cancel': [('readonly', False)]})
    as_fecha_caducidad = fields.Datetime(string="Fecha caducidad", store=True, readonly=True, compute='_fecha_caducidad')

    @api.multi
    def cancelar_venta(self):
        #facturada
        pick_del = []
        imediate_obj=self.env['stock.immediate.transfer']
        for sol in self.order_line:
            self._cr.execute("SELECT rel.invoice_line_id FROM sale_order_line_invoice_rel rel WHERE rel.order_line_id = %s" %str(sol.id))
            res_consulta=[x for x in self._cr.fetchall()]
            _logger.debug("\n ID de la linea de factura: %s\n", str(res_consulta))
            if res_consulta:
                if self.env['account.invoice.line'].sudo().search([('id','=',res_consulta[0][0])]).invoice_id.order_status == 'valida':
                    raise UserError(_("El pedido de venta tiene una o mas facturas VALIDAS.\n Por favor ANULAR la(s) factura(s) si necesita realizar cambios."))
        
        #cancelar y devorlver productos a inventario
        if self.picking_ids:
            #acumulamos los pìcking a cancelar pero primero se genera un retorno de cada uno de ellos 
            for picking_id in self.picking_ids:
                if picking_id.state == 'done':
                    pick_del.append(picking_id.id)
                else:
                    picking_id.action_cancel()
            #generar retorno de los picking a cancelar
            for picking_id in self.picking_ids:
                if picking_id.state == 'done':
                    StockReturnPicking = self.env['stock.return.picking']
                    default_data = StockReturnPicking.with_context(active_ids=picking_id.ids, active_id=picking_id.id).default_get(['move_dest_exists', 'original_location_id', 'product_return_moves', 'parent_location_id', 'location_id'])
                    return_wiz = StockReturnPicking.with_context(active_ids=picking_id.ids, active_id=picking_id.id).create(default_data)
                    res = return_wiz.create_returns()
                    return_pick = self.env['stock.picking'].browse(res['res_id'])
                    for picking_lines in return_pick.move_ids_without_package:
                        picking_lines.qty_done = picking_lines.product_qty
                    return_pick.action_assign()
                    return_pick.action_done()
            #Se consultan los picking  a borrar
            cancelar_picking = self.env['stock.picking'].search([('id','in',tuple(pick_del))])
            for picking_for_delete in cancelar_picking:
                picking_for_delete.write({'state':'cancel'})
            #Se borran las lineas de los picking cancelados
            for picking in self.picking_ids:
                if picking.state == 'assigned':
                    picking.action_confirm()
                    picking.action_assign()
                    imediate_rec=imediate_obj.create({'pick_ids': [(4, picking.id)]})
                    imediate_rec.process()
            for picking in self.picking_ids:
                if picking.state == 'assigned':
                    picking.action_confirm()
                    picking.action_assign()
                    imediate_rec=imediate_obj.create({'pick_ids': [(4, picking.id)]})
                    imediate_rec.process()
            for pickin_borrar in self.picking_ids:
                if pickin_borrar.state == 'done':
                    for move in pickin_borrar.move_lines:
                        move.write({'state':'cancel'})
                    pickin_borrar.write({'state':'cancel'})
            if pick_del:
                self.env.cr.execute("DELETE FROM stock_move WHERE picking_id IN %s;",
                                    ([tuple(pick_del)]))
                self.env.cr.execute("DELETE FROM stock_move_line WHERE picking_id IN %s;",
                                    ([tuple(pick_del)]))
                self.env.cr.execute("UPDATE stock_picking SET state = 'cancel' WHERE id IN %s;",
                                    ([tuple(pick_del)]))
                # if return_pick:
                #     self.env.cr.execute("DELETE FROM stock_picking WHERE id IN %s;", ([tuple(return_pick.ids)]))
                #     self.env.cr.execute("DELETE FROM stock_move WHERE picking_id IN %s;", ([tuple(return_pick.ids)]))
                #     self.env.cr.execute("DELETE FROM stock_move_line WHERE picking_id IN %s;", ([tuple(return_pick.ids)]))
        self.write({'state':'cancel'})


    @api.multi
    def imprimir_nota_remision(self):
        return self.env.ref('as_sales.as_nota_pedido_qweb_pdf').report_action(self)

    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion = {
            'nombre_empresa' : self.company_id.name or '',
            'nit' : self.company_id.vat or '',
            'direccion1' : self.company_id.street or '',
            'telefono' : self.company_id.phone or '',
            'ciudad' : self.company_id.city or '',
            'pais' : self.company_id.country_id.name or '',
        }
        moduleFactura = self.env['ir.module.module'].sudo().search(
            [("name","=","as_invoice_2116"),("state","=","installed")])
        if moduleFactura:
            if self.dosificacion:
                diccionario_dosificacion = {
                    'nombre_empresa' : self.dosificacion.nombre_empresa or '',
                    'nit' : self.dosificacion.nit_empresa or '',
                    'direccion1' : self.dosificacion.direccion1 or '',
                    'telefono' : self.dosificacion.telefono or '',
                    'ciudad' : self.dosificacion.ciudad or '',
                    'pais' : self.company_id.country_id.name or '',
                }
        info = diccionario_dosificacion[str(requerido)]
        return info

    def convertir_numero_a_literal(self, amount):
        amt_en = as_amount_to_text_es.amount_to_text(amount, 'BOB')
        return amt_en

    @api.multi
    def _obtener_total_descuento(self,order_id):
        order_line = self.env['sale.order.line'].sudo().search([('order_id', '=', order_id)])
        monto=0.00
        monto_discount=0.00
        for line in order_line:
            if line.discount > 0.00:
                monto = (line.price_unit * line.product_uom_qty)
                monto_discount += (monto*line.discount)/100
        return monto_discount

    def amount_neto(self,order_id):
        order_line = self.env['sale.order.line'].sudo().search([('order_id', '=', order_id)])
        monto=0.00
        for line in order_line:
            monto += (line.price_unit * line.product_uom_qty)
        return float_round(monto-self._obtener_total_descuento(order_id), precision_rounding=self.currency_id.rounding)
        
    def amount_bruto(self,order_id):
        order_line = self.env['sale.order.line'].sudo().search([('order_id', '=', order_id)])
        monto=0.00
        for line in order_line:
            monto += (line.price_unit * line.product_uom_qty)
        return monto

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    @api.onchange('as_scan_packet')
    def escanear_codigo_packet(self):
        self.ensure_one()
        if self.as_scan_packet:
            array = (self.as_scan_packet)
            product_packaging = self.env['product.packaging'].sudo().search([('barcode', '=', array)],limit=1)
            if not product_packaging:
                raise UserError(_("Producto no encontrado verifique su etiqueta, de codigo de producto %s") % array) 
            self.product_id = product_packaging.product_id
            self.product_uom_qty = self.product_uom_qty + product_packaging.qty
            self.as_scan_packet = None


    as_stock_fisico_actual = fields.Float('Stock Actual', compute='_detalle_producto', help=u'Stock disponible actual del producto.')
    as_stock_virtual_actual = fields.Float('Stock Previsto', compute='_detalle_producto', help=u'Stock disponible actual del producto.')
    as_tiempo_entrega_producto = fields.Many2one('as.plazo.entrega.productos', string="Entrega Aprox")
    analytic_tag_ids = fields.Many2many(default=lambda self: self._default_analytic_ids())
    as_scan_packet = fields.Char(string="Escanear Paquetes", help="Click aqui para que el cursor lea el codigo de paquete y cargar producto")

    @api.model
    def _default_analytic_ids(self):
        analytic_obj = self.env['account.analytic.tag']
        analytic = analytic_obj.search( [('name', '=', 'Ingresos por Ventas')])
        if analytic:
            analytic_id = analytic_obj.search( [('name', '=', 'Ingresos por Ventas')]).id
            analytic_id = analytic_id or False
            return [analytic_id]

    # Devuelve domain de UoM de venta de cada producto
    @api.onchange('discount')
    def _change_product_discount(self):
        if float(self.order_id.partner_id.as_discount) > 0:
            if self.discount > float(self.order_id.partner_id.as_discount):
                self.discount= float(self.order_id.partner_id.as_discount)

    # Devuelve domain de UoM de venta de cada producto
    @api.onchange('product_id')
    def _change_product_oum_sale(self):
        ids = self.product_id.as_uom_so_ids.ids or []
        return {'domain': {'product_uom': [('id', 'in', tuple(ids))]}}

    # Se hereda funcion core para agregar UoM por defecto desde el campo 'as_uom_so_ids' 
    # de product.template
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = list(self.product_id.attribute_line_ids)
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
           if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            # Se agrega el primer valor de UoM para venta del producto
            vals['product_uom'] = self.product_id.as_uom_so_ids[0] if self.product_id.as_uom_so_ids else None
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
           quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))
        self._compute_tax_id()
        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

    #carga los stock por ruta en lines de epedidos de venta
    @api.onchange('product_id','route_id')
    def _detalle_producto(self):
        rutas_habilitadas = self.user_has_groups('sale_stock.group_route_so_lines')
        for record in self:
            if record:
                if record.order_id.partner_id:
                    for producto in record:
                        if record.id == producto.id:
                            # _logger.info('\n\n %r \n\n', [moduleObj,record.route_id])
                            previsto = producto.product_id.virtual_available
                            if (producto.product_id.id and record.route_id):
                                cantidad= producto.product_id.with_context(location=[record.route_id.rule_ids[0].location_src_id.id]).qty_available
                                previsto =  producto.product_id.with_context(location=[record.route_id.rule_ids[0].location_src_id.id]).virtual_available
                                record.as_stock_fisico_actual = cantidad
                            else:
                                # Cuando tengamos el modulo de inventarios pero no estemos trabajando con rutas, mostraremos la cantidad total del producto en todas las ubicaciones
                                if rutas_habilitadas != False:
                                    cant_almacen_producto = self.env['stock.quant'].search([('product_id','=',producto.product_id.id)])
                                    stock_total = 0
                                    stock_virtual_total = 0
                                    if cant_almacen_producto:
                                        for cant_total_almacenada in cant_almacen_producto:
                                            stock_total = cant_total_almacenada.quantity + stock_total
                                            stock_virtual_total = cant_total_almacenada.reserved_quantity + stock_virtual_total
                                    cantidad = stock_total if cant_almacen_producto else 0.0
                                    previsto = stock_virtual_total if cant_almacen_producto else 0.0
                                    record.as_stock_fisico_actual = cantidad
                                else:
                                    record.as_stock_fisico_actual = producto.product_id.qty_available
                            record.as_stock_virtual_actual = previsto

    @api.onchange('product_id', 'product_uom_qty')
    def _alcambiar_producto_plazo_entrega(self):
        entrega_inmediata=self.env['as.plazo.entrega.productos'].sudo().search([("as_name_texto","=","Inmediata")])
        plazo_desconocido=self.env['as.plazo.entrega.productos'].sudo().search([("as_name_texto","=","Desconocido")])

        if (not entrega_inmediata):
            vals={'as_espera_minima':0, 'as_espera_maxima':0, 'as_name_texto':'Inmediata'}
            entrega_inmediata=self.env['as.plazo.entrega.productos'].sudo().create(vals)

        if (not plazo_desconocido):
            vals={'as_espera_minima':0, 'as_espera_maxima':0, 'as_name_texto':'Desconocido'}
            plazo_desconocido=self.env['as.plazo.entrega.productos'].sudo().create(vals)

        if self.as_stock_fisico_actual >= self.product_uom_qty:
            self.as_tiempo_entrega_producto = entrega_inmediata[0]
        elif self.product_id.as_plazo_entrega: 
            self.as_tiempo_entrega_producto = self.product_id.as_plazo_entrega
        elif (not self.product_id.as_plazo_entrega):
            self.as_tiempo_entrega_producto = plazo_desconocido[0]

    @api.onchange('product_id')
    def _rutas_dominio(self):
        for route in self:
            ubicaciones=[]
            rutas_habilitadas = self.user_has_groups('sale_stock.group_route_so_lines')
            if rutas_habilitadas:
                rutas_permitidas=[]
                if self.env.user.as_default_route:
                    ubicaciones.append(self.env.user.as_default_route.id)
                    self.env.cr.execute("SELECT id FROM stock_location_route where sale_selectable='True'")
                    rutas=self.env.cr.fetchall()
                    for ruta in rutas:
                        ubicaciones.append(ruta[0])
                    for i in ubicaciones:
                        if i not in rutas_permitidas:
                            rutas_permitidas.append(i)
                else:
                    self.env.cr.execute("SELECT id FROM stock_location_route where sale_selectable='True'")
                    rutas=self.env.cr.fetchall()
                    if rutas:
                        for ruta in rutas:
                            if ruta.sale_selectable == True:
                                rutas_permitidas.append(ruta.id)       
                if rutas_permitidas:
                    if len(rutas_permitidas)>0:
                        self.update({
                            'route_id': rutas_permitidas[0],
                        })
                #return  [('id', 'in', tuple(rutas_permitidas))]
                return {'domain':{'route_id': [('id','in', tuple(rutas_permitidas))]}}
            else:
                return []

    route_id = fields.Many2one('stock.location.route', string='Ruta', domain=_rutas_dominio)

