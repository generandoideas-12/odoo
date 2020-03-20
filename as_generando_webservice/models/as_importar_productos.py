# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from tabulate import tabulate
import pandas as pd
import csv
import base64
from io import StringIO

from werkzeug.urls import url_encode

# Spider
import requests, json
from itertools import islice
import time

headers="keys"

import logging
_logger = logging.getLogger(__name__)

class as_importar_productos(models.Model):
    _name = "as.importar.productos"
    _description = 'Importador de Productos'
    _inherit = ['mail.thread']
    _order = "write_date desc"
    
    name = fields.Char('Comentario', default='Importacion manual')
    as_url = fields.Char('Endpoint', default='https://www.generandoideas.com/conexionodoo/esi_api/productos')
    as_url_full = fields.Char('Full Endpoint', default='https://www.generandoideas.com/conexionodoo/esi_api/productos')
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
    def update_product(self):
        # product_obj = self.env['product.product'].search([('id','=',ids.id)],limit=1)
        # ids.update({
        #     'as_costo_anterior':product_obj.as_costo_proveedor
        # })

        self.env.cr.execute("""
            select pp.id, pt.name, pt.as_codigo_proveedor, pt.as_costo_proveedor, pt.as_costo_anterior, pt.as_name_proveedor, pt.as_existencias, pt.list_price, pt.as_factor, pt.as_descontinuado from product_product pp, product_template pt where tf_check_update = 'no_update' and pp.product_tmpl_id = pt.id limit %s
        """%self.as_iteracion)
        result = self.env.cr.dictfetchall()

        vals = {
            'name':values.get('NOMPROD'),
            'as_codigo_proveedor':values.get('CODPROD'),
            'as_costo_proveedor':float(values.get('COSUNIT')),

            'as_costo_anterior': float(values.get('COSUNIT')),

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
            # 'standard_price':float(values.get('COSUNIT')),
            'as_existencias':values.get('EXISTENCIAS'),
            'as_name_proveedor':values.get('PROVEEDOR'),
            'list_price':float(values.get('COSUNIT'))*(1+self.as_factor),
            'as_factor':float(self.as_factor),
            'as_descontinuado':False,
            'sale_ok':True,
            'purchase_ok':True,
            'as_costo_anterior':float(0.00),
            'tf_check_update': 'no_update',
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

    def importar_productos(self, value):
        # self.descontinuar()
        importar = self.env['as.importar.productos'].search([('as_activo','=', True)],order="write_date asc", limit=1)
        
        
        for operacion in importar:
            # marcar fecha como procesado
            today = fields.Datetime.now(self)
            operacion.write_date = today
            self.env.cr.commit()
            
            # procesar URL
            response = requests.get(operacion.as_url,auth=requests.auth.HTTPBasicAuth(operacion.as_login,operacion.as_password))
            jsondata = json.loads(response.text)
            
            # Full Json Data
            response2 = requests.get(operacion.as_url_full,auth=requests.auth.HTTPBasicAuth(operacion.as_login,operacion.as_password))
            jsondata2 = json.loads(response2.text)
            
            if operacion.as_catalogo in jsondata:
                
                jsondata = jsondata[operacion.as_catalogo]
                jsondata2 = jsondata2[operacion.as_catalogo]
                
                jsondata = self.take(operacion.as_limit, jsondata)
                
                print(jsondata)

                keys = ['CODPROD','NOMPROD','COSUNIT','EXISTENCIAS','PROVEEDOR']

                count = 0
                counter = 0
                total_elapsed = 0
                nro_orders = len(jsondata)

                if value.get('create_tf'):
                    self.env.cr.execute("""select as_codigo_proveedor from product_template """)
                    product_result = self.env.cr.dictfetchall()

                    productos = [x['as_codigo_proveedor'] for x in product_result]

                    new_json_data = [y for y in jsondata if y['CODPROD'] not in productos]
                    for value in new_json_data:
                        # Inicializar tiempo

                        elapsed = 0
                        start = time.time()
                        time.clock()

                        if value:
                            # product_ids = self.env['product.product'].search([('as_codigo_proveedor','=', value.get('CODPROD'))],limit=1)
                            # product_ids = self.obtener_producto(productos,value.get('CODPROD'))
                            # if product_ids:
                            #     res = self.update_product(product_ids,value)
                            #     tipo_operacion = 'UPDATE'
                            # else:
                            res = self.create_product(value)
                            tipo_operacion = 'CREATE'
                            count += 1
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

                        # if counter == operacion.as_iteracion:
                        #     break

                        _logger.info("\n\nNro: %s Operacion: %s Porcentaje: %s Registro confirmado: %s Segundos: %s TOTAL TIEMPO: %s URL: %s", counter, tipo_operacion, percentage, value.get('CODPROD'), elapsed, round((total_elapsed/60),2), operacion.as_url)

                elif value.get('update_tf'):

                    self.env.cr.execute("""select as_codigo_proveedor from product_template """)
                    product_result = self.env.cr.dictfetchall()

                    productos = [x['as_codigo_proveedor'] for x in product_result]

                    old_json_data = [z for z in jsondata if z['CODPROD'] in productos]

                    self.env.cr.execute("""
                                select pp.id, pt.name, pt.as_codigo_proveedor, pt.as_costo_proveedor, pt.as_costo_anterior, pt.as_name_proveedor, pt.as_existencias, pt.list_price, pt.as_factor, pt.as_descontinuado from product_product pp, product_template pt where pp.product_tmpl_id = pt.id -- limit %s
                            """ % (self.as_iteracion+150))
                    result = self.env.cr.dictfetchall()
                    
                    count = 1
                    
                    _logger.info('Updating Started')
                    for value in result:

                        elapsed = 0
                        start = time.time()
                        time.clock()
                        tipo_operacion = 'UPDATE'
                        

                        search_res = [x for x in old_json_data if x['CODPROD'] == value['as_codigo_proveedor']]
                        if search_res:
                            values = search_res[0]
                            pro_id = self.env['product.product'].browse(value['id']).write({
                                'name':values.get('NOMPROD'),
                                'as_codigo_proveedor':values.get('CODPROD'),
                                'as_costo_proveedor':float(values.get('COSUNIT')),
                                # 'standard_price':float(values.get('COSUNIT')),
                                'as_existencias':values.get('EXISTENCIAS'),
                                'as_name_proveedor':values.get('PROVEEDOR'),
                                'list_price':float(values.get('COSUNIT'))*(1+self.as_factor),
                                'as_factor':float(self.as_factor),
                                'as_descontinuado':False,
                                'sale_ok':True,
                                'purchase_ok':True,
                                'as_costo_anterior':float(value['as_costo_proveedor']),
                                'tf_check_update': 'update',
                                # 'default_code':values.get('PROVEEDOR'),
                            })

                            # _logger.info('Update number %s'%str(count))
                            # _logger.info('Product Info')
                            # _logger.info(pro_id)
                            
                            # Escribir cada cierta iteracion
                            if count == operacion.as_iteracion:
                                self.env.cr.commit()
                                count = 0                            
                            count+=1

                            # Tiempo transcurrido
                            elapsed = round((time.time() - start),2)
                            total_elapsed = elapsed + total_elapsed
                            counter = counter + 1
                            percentage = round(float(counter) / nro_orders * 100,2)

                            _logger.info("\n\nNro: %s Producto: %s Operacion: %s Porcentaje: %s Registro confirmado: %s Segundos: %s TOTAL TIEMPO: %s URL: %s", counter, value['name'], tipo_operacion, percentage, value.get('CODPROD'), elapsed, round((total_elapsed/60),2), operacion.as_url)

                    if not result:
                        _logger.info('All Product set to state no update!')
                        self.env.cr.execute("""update product_template set tf_check_update = 'no_update';""")

                    # self.env.cr.commit()

                    # elapsed = round((time.time() - start), 2)
                    # total_elapsed = elapsed + total_elapsed
                    # counter = counter + 1
                    # percentage = round(float(counter) / nro_orders * 100, 2)

                    # if counter == operacion.as_iteracion:
                    #     break

                    # _logger.info(
                    #     "\n\nNro: %s Operacion: %s Porcentaje: %s Registro confirmado: %s Segundos: %s TOTAL TIEMPO: %s",
                    #     counter, tipo_operacion, percentage, value.get('CODPROD'), elapsed,
                    #     round((total_elapsed / 60), 2))

                operacion.as_resultado = True
                
                body =  "<b>Total Productos Remotos: </b>%s <br>" %(len(jsondata))
                body += "<b>Total Productos Locales: </b>%s <br>" %(str(self.as_total_productos_actuales()))
                body += "<b>Tiempo (Segundos): </b>%s <br>" %(round(total_elapsed,2))
                
                ## JSON
                attach_id = self.as_generar_csv(jsondata,"datos_remotos" + str(operacion.id) + ".csv")
                attach_url = "<a href='/web/content/" + str(attach_id.id) + "?download=true' download='Datos Remotos JSON " + str(attach_id.id) + "'>Datos Remotos JSON " + str(attach_id.id) + "</a>"
                # table = tabulate(jsondata,headers,tablefmt='html')
                # table = table.replace('<table>', '<table class="oe_list_content" border="1" style="border-collapse:collapse;">')
                body += "<b>Datos REST Importados: </b></br>%s <br>" %(attach_url)
                
                ## DIFERENCIAS
                # table_diferencias = tabulate(self.as_diferencias(jsondata),headers,tablefmt='html')
                # table_diferencias = table_diferencias.replace('<table>', '<table class="oe_list_content" border="1" style="border-collapse:collapse;">')
                # body += "<b>DIFERENCIA entre DB LOCAL y Remoto: </b></br>%s <br>" %(table_diferencias)
                ## Crear CSV
                # table_diferencias = self.as_diferencias(jsondata2)
                # attach_id2 = self.as_generar_csv2(table_diferencias,"datos_diferencias" + str(operacion.id) + ".csv",True)
                # attach_url2 = "<a href='/web/content/" + str(attach_id2.id) + "?download=true' download='Datos Remotos JSON " + str(attach_id2.id) + "'>Datos Remotos " + str(attach_id2.id) + "</a>"
                # body += "<b>DIFERENCIA entre DB LOCAL y Remoto sin paginacion: </b></br>%s <br>" %(attach_url2)
                
                ## JSON UNICOS
                # table_unicos = tabulate(self.as_remover_duplicados(jsondata),headers,tablefmt='html')
                # table_unicos = table_unicos.replace('<table>', '<table class="oe_list_content" border="1" style="border-collapse:collapse;">')
                # body += "<b>REST Importados Unicos: </b></br>%s <br>" %(table_unicos)
                ## Crear CSV
                # table_unicos = self.as_remover_duplicados(jsondata)
                # attach_id3 = self.as_generar_csv(table_unicos,"table_unicos" + str(operacion.id) + ".csv")
                # attach_url3 = "<a href='/web/content/" + str(attach_id.id) + "?download=true' download='Datos Remotos JSON " + str(attach_id.id) + "'>Datos Remotos " + str(attach_id.id) + "</a>"
                # body += "<b>REST Importados Unicos: </b></br>%s <br>" %(attach_url3)
                
                ## JSON DUPLICADOS
                # table_duplicados = tabulate(self.as_duplicados(jsondata),headers,tablefmt='html')
                # table_duplicados = table_duplicados.replace('<table>', '<table class="oe_list_content" border="1" style="border-collapse:collapse;">')
                # body += "<b>REST Importados Duplicados: </b></br>%s <br>" %(table_duplicados)
                ## Crear CSV
                # table_duplicados = self.as_duplicados(jsondata)
                # attach_id4 = self.as_generar_csv2(table_duplicados,"table_duplicados" + str(operacion.id) + ".csv",True)
                # attach_url4 = "<a href='/web/content/" + str(attach_id4.id) + "?download=true' download='REST Importados Duplicados " + str(attach_id4.id) + "'>REST Importados Duplicados " + str(attach_id4.id) + "</a>"
                # body += "<b>REST Importados Duplicados: </b></br>%s <br>" %(attach_url4)
                
                ## LOCAL DUPLICADOS
                # table_duplicados_local = tabulate(self.as_repetidos(),headers,tablefmt='html')
                # table_duplicados_local = table_duplicados_local.replace('<table>', '<table class="oe_list_content" border="1" style="border-collapse:collapse;">')
                # body += "<b>DB Duplicados: </b></br>%s <br>" %(table_duplicados_local)
                ## Crear CSV
                # table_duplicados_local = self.as_repetidos()
                # attach_id5 = self.as_generar_csv2(table_duplicados_local,"table_duplicados_local" + str(operacion.id) + ".csv",False)
                # attach_url5 = "<a href='/web/content/" + str(attach_id5.id) + "?download=true' download='DB Duplicados " + str(attach_id5.id) + "'>DB Duplicados " + str(attach_id5.id) + "</a>"
                # body += "<b>DB Duplicados: </b></br>%s <br>" %(attach_url5)

                # body += 
                operacion.message_post(body = body)
            
            else:
                # operacion.write_date = today
                operacion.as_resultado = False
                # operacion.as_activo = True
            #     raise ValidationError(
            #         _("Valor en 'Catalogo JSON' Incorrecto: " + operacion.as_catalogo))
                
    # LOCAL Repetidos 
    def as_repetidos(self):
        query = """
        select a.producto as "CODPROD",a.nombre as "NOMPROD", a.repetidos from (select as_codigo_proveedor as producto, name as nombre, count(id) as repetidos from product_template group by 1,2 order by 3 desc) as a where a.repetidos > 1 and producto is not null;
        """
        self.env.cr.execute(query)
        repetidos = self.env.cr.dictfetchall()
        return repetidos
    
    # LOCAL Total Productos 
    def as_total_productos_actuales(self):
        query = """
        select count(id) as cuenta from product_template;
        """
        self.env.cr.execute(query)
        repetidos = self.env.cr.fetchall()
        return repetidos[0][0]
    
    def as_productos_actuales(self):
        query = """
        select a.as_codigo_proveedor as "CODPROD",a.name as "NOMPROD" from product_template as a where a.as_codigo_proveedor is not null;
        """
        self.env.cr.execute(query)
        productos = self.env.cr.dictfetchall()
        return productos    
    
    def as_remover_duplicados(self,data):
        df = pd.DataFrame(data,columns=['CODPROD', 'NOMPROD'])
        df.sort_values("CODPROD", inplace = True)
        df.drop_duplicates(subset ="CODPROD", keep = False, inplace = True) 
        return df
    
    def as_duplicados(self,data):
        df = pd.DataFrame(data,columns=['CODPROD', 'NOMPROD'])
        duplicated_df=df[df.CODPROD.duplicated(keep=False)]
        return duplicated_df
    
    def as_diferencias(self,json):
        df2=pd.DataFrame(json)
        df1=pd.DataFrame(self.as_productos_actuales())
        df1.sort_values("CODPROD", inplace = True)
        df2.sort_values("CODPROD", inplace = True)
        
        df_1notin2 = df1[~(df1['CODPROD'].isin(df2['CODPROD']) & df1['NOMPROD'].isin(df2['NOMPROD']))].reset_index(drop=True)
        return df_1notin2

    def as_eliminar_adjuntos(self,operacion):
        self.env['ir.attachment'].search([('res_model','=','as.importar.productos'),('res_id','=',self.id)]).unlink()
    
    @api.multi
    def as_activar_todo(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        products = self.env['as.importar.productos'].browse(active_ids)
        for product in products:
            if product.as_activo:
                product.as_activo = False
            else:
                product.as_activo = True

        
    def as_generar_csv(self,x,filename):
        archivo = StringIO()
        f = csv.writer(archivo)

        # Write CSV Header, If you dont need that, remove this line
        f.writerow([
            'CODPROD',
            'NOMPROD',
            'COSUNIT',
            'EXISTENCIAS',
            'PROVEEDOR'
        ])

        for x in x:
            f.writerow([
                x["CODPROD"],
                x["NOMPROD"],
                x["COSUNIT"],
                x["EXISTENCIAS"],
                x["PROVEEDOR"],
            ])
            
        # file_data = f.read()
        out = base64.encodestring(bytes(archivo.getvalue(), encoding = 'utf-8'))
        
        # csv.writer(archivo)
        
        attach_id = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': out,
            'res_model': 'as.importar.productos',
            'res_id': self.id,
            'mimetype': 'text/csv'
        })
        
        return attach_id
    
    def as_generar_csv2(self,x,filename,panda=True):

        if panda:
            x = x.values.tolist()

        archivo = StringIO()
        f = csv.writer(archivo)

        # Write CSV Header, If you dont need that, remove this line
        f.writerow([
            'CODPROD',
            'NOMPROD',
        ])

        for y in x:
            f.writerow([
                y[0],
                y[1],
            ])
            
        # file_data = f.read()
        out = base64.encodestring(bytes(archivo.getvalue(), encoding = 'utf-8'))
        
        # csv.writer(archivo)
        
        attach_id = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': out,
            'res_model': 'as.importar.productos',
            'res_id': self.id,
            'mimetype': 'text/csv'
        })
        
        return attach_id