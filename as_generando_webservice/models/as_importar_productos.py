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

# Spider
import requests, json
from itertools import islice
import time



import logging
_logger = logging.getLogger(__name__)

class as_importar_productos(models.Model):
    _name = "as.importar.productos"
    _description = 'Importador de Productos'
    _inherit = ['mail.thread']
    _order = "write_date desc"
    
    name = fields.Char('Comentario', default='Importacion manual')
    as_url = fields.Char('Endpoint', default='https://www.generandoideas.com/conexionodoo/esi_api/productos')
    as_login = fields.Char('Usuario', default='admin')
    as_password = fields.Char('Password', default='eIsTi_1987API')
    as_iteracion = fields.Integer('Frecuencia de almacenamiento', default=100)
    as_limit = fields.Integer('Limite', default=10000)
    as_resultado = fields.Boolean('Resultado', default=False, readonly=True)
    as_activo = fields.Boolean('Activado', default=False, readonly=True)
    as_factor = fields.Float('Factor Precio', default=1)
    as_catalogo = fields.Char('Catalogo JSON', default='response')

    def activar(self):
        # query = """
        #     UPDATE as_importar_productos
        #         SET as_activo = False
        # """
        # self.env.cr.execute(query)
        if self.as_activo:
            self.as_activo = False
        else:
            self.as_activo = True

    def descontinuar(self):
        query = """
            UPDATE product_template
                SET as_descontinuado = True
        """
        self.env.cr.execute(query)

    def validacion_numero(self,valor, tipo):
        try:
            resultado = tipo(valor)
        except:
            resultado = 0
        return resultado


    def take(self, n, iterable):
        "Return first n items of the iterable as a list"
        return list(islice(iterable, n))

    @api.multi
    def update_product(self, ids, values):
        product_obj = self.env['product.product'].search([('id','=',ids.id)],limit=1)
        ids.update({
            'as_costo_anterior':product_obj.as_costo_proveedor
        })
        vals = {
            'name':values.get('NOMPROD'),
            'as_codigo_proveedor':values.get('CODPROD'),
            'as_costo_proveedor':float(values.get('COSUNIT')),
            'as_name_proveedor':values.get('PROVEEDOR'),
            'as_existencias':values.get('EXISTENCIAS'),
            'list_price':float(values.get('COSUNIT'))*(1+self.as_factor),
            'as_factor':float(self.as_factor),
            'as_descontinuado':False,
            # 'default_code':values.get('PROVEEDOR'),
        }
        # _logger.debug("\n\nValores update_product: %s \n\nIDs: %s", str(vals), ids)
        # _logger.debug("Valores create_product: %s", str(vals))
        res = ids.update(vals)
        return res
    
    @api.multi
    def create_product(self, values):
        product_obj = self.env['product.product']
        vals = {
            'name':values.get('NOMPROD'),
            'as_codigo_proveedor':values.get('CODPROD'),
            'as_costo_proveedor':float(values.get('COSUNIT')),
            'as_existencias':values.get('EXISTENCIAS'),
            'as_name_proveedor':values.get('PROVEEDOR'),
            'list_price':float(values.get('COSUNIT'))*(1+self.as_factor),
            'as_factor':float(self.as_factor),
            'as_descontinuado':False,
            'as_costo_anterior':float(0.00),
            
            # 'default_code':values.get('PROVEEDOR'),
        }
        # _logger.debug("Valores create_product: %s", str(vals))
        res = product_obj.create(vals)
        return res

    def obtener_producto(self,productos,producto):
        for prod in productos:
            if prod.as_codigo_proveedor == producto:
                return productos
        return False

    def importar_productos(self):
        self.descontinuar()
        importar = self.env['as.importar.productos'].search([('as_activo','=', True)])
        for operacion in importar:
            response = requests.get(operacion.as_url,auth=requests.auth.HTTPBasicAuth(operacion.as_login,operacion.as_password))
            jsondata = json.loads(response.text)
            
            if operacion.as_catalogo in jsondata:
                
                jsondata = jsondata[operacion.as_catalogo]
                
                jsondata = self.take(operacion.as_limit, jsondata)
                
                print(jsondata)

                keys = ['CODPROD','NOMPROD','COSUNIT','EXISTENCIAS','PROVEEDOR']

                count = 0
                counter = 0
                total_elapsed = 0
                nro_orders = len(jsondata)

                productos = self.env['product.product'].search([])
                
                for value in jsondata:
                    # Inicializar tiempo
                    count += 1
                    elapsed = 0
                    start = time.time()
                    time.clock() 
                    
                    if value:
                        product_ids = self.env['product.product'].search([('as_codigo_proveedor','=', value.get('CODPROD'))],limit=1)
                        # product_ids = self.obtener_producto(productos,value.get('CODPROD'))
                        if product_ids:
                            res = self.update_product(product_ids,value)
                            tipo_operacion = 'UPDATE'
                        else:
                            res = self.create_product(value)
                            tipo_operacion = 'CREATE'                    
                            # raise Warning(_('"%s" Product not found.') % values.get('default_code'))
                    
                    # Escribir cada cierta iteracion
                    if count == operacion.as_iteracion:
                        self.env.cr.commit()
                        count = 0
                        
                    # Tiempo transcurrido
                    elapsed = round((time.time() - start),2)
                    total_elapsed = elapsed + total_elapsed
                    counter = counter + 1
                    percentage = round(float(counter) / nro_orders * 100,2)
                    _logger.info("\n\nNro: %s Operacion: %s Porcentaje: %s Registro confirmado: %s Segundos: %s TOTAL TIEMPO: %s", counter, tipo_operacion, percentage, value.get('CODPROD'), elapsed, round((total_elapsed/60),2))

                operacion.as_resultado = True
                body="<b>Nro registros: </b>%s <b>Tiempo: </b>%s<br>" %(len(jsondata),total_elapsed)
                operacion.message_post(body = body, content_subtype='html')

            else:
                raise ValidationError(
                    _("Valor en 'Catalogo JSON' Incorrecto: " + operacion.as_catalogo))