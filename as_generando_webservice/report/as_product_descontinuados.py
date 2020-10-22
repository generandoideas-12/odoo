# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime

class as_product_descontinuados_excel(models.AbstractModel):
    _name = 'report.as_generando_webservice.product_descontinuados.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

      #Definiciones generales del archivo, formatos, titulos, hojas de trabajo
      sheet = workbook.add_worksheet('Detalle de Movimientos')
      titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold':True })
      titulo1.height = 20 * 50
      titulo2 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
      titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
      titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
      titulo4 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })

      number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00'})
      number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00'})
      number_right_bold = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
      number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
      number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
      number_right_col.set_locked(False)

      letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
      letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
      letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
      letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
      letter5 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True, 'bold': True})
      letter_locked = letter3
      letter_locked.set_locked(False)

      # Aqui definimos en los anchos de columna
      sheet.set_column('A:A',10, letter1)
      sheet.set_column('B:B',30, letter1)
      sheet.set_column('C:C',30, letter1)
      sheet.set_column('D:D',30, letter1)
      sheet.set_column('E:E',30, letter1)

      # titulos
      sheet.merge_range('A1:E1', 'PRODUCTOS DESCONTINUADOS', titulo1)
      sheet.set_row(0, 40)
      sheet.write(1, 0, 'Fecha y Hora',titulo3)
      sheet.write(1, 1, datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
      filas=4
      sheet.write(filas, 0, 'N',titulo2)
      sheet.write(filas, 1, 'Codigo Proveedor',titulo2)
      sheet.write(filas, 2, 'Nombre del Producto',titulo2)
      sheet.write(filas, 3, 'Codigo Producto Interno',titulo2)
      sheet.write(filas, 4, 'Nombre del Proveedor',titulo2)
      productos = self.env['product.product'].search([('as_descontinuado','=',True)])
      filas+=1   
      cont=0   
      for product in productos:
        cont+=1
        sheet.write(filas, 0, cont)
        sheet.write(filas, 1, product.as_codigo_proveedor)
        sheet.write(filas, 2, product.name)
        sheet.write(filas, 3, product.default_code)
        sheet.write(filas, 4, product.as_name_proveedor)
        filas+=1


class as_product_price_excel(models.AbstractModel):
    _name = 'report.as_generando_webservice.product_price.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

      #Definiciones generales del archivo, formatos, titulos, hojas de trabajo
      sheet = workbook.add_worksheet('Detalle de Movimientos')
      titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold':True })
      titulo1.height = 20 * 50
      titulo2 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
      titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
      titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
      titulo4 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })

      number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00'})
      number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00'})
      number_right_bold = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
      number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
      number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
      number_right_col.set_locked(False)

      letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
      letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
      letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
      letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
      letter5 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True, 'bold': True})
      letter_locked = letter3
      letter_locked.set_locked(False)

      # Aqui definimos en los anchos de columna
      sheet.set_column('A:A',10, letter1)
      sheet.set_column('B:B',20, letter1)
      sheet.set_column('C:C',30, letter1)
      sheet.set_column('D:D',20, letter1)
      sheet.set_column('E:E',20, letter1)
      sheet.set_column('F:F',20, letter1)
      sheet.set_column('G:G',20, letter1)
      sheet.set_column('H:H',20, letter1)
      sheet.set_column('I:I',20, letter1)

      # titulos
      sheet.merge_range('A1:I1', 'REPORTE CAMBIO EN PRECIOS', titulo1)
      sheet.set_row(0, 40)
      sheet.write(1, 0, 'Fecha y Hora',titulo3)
      sheet.write(1, 1, datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

      filas=4
      sheet.write(filas, 0, 'N',titulo2)
      sheet.write(filas, 1, 'Codigo Proveedor',titulo2)
      sheet.write(filas, 2, 'Nombre del Producto',titulo2)
      sheet.write(filas, 3, 'Codigo Producto Interno',titulo2)
      sheet.write(filas, 4, 'Coste Anterior',titulo2)
      sheet.write(filas, 5, 'Costo Producto',titulo2)
      sheet.write(filas, 6, 'Nombre del Proveedor',titulo2)
      sheet.write(filas, 7, 'Aumento precio MXN',titulo2)
      sheet.write(filas, 8, 'Aumento en porcentaje',titulo2)
      productos = self.env['product.product'].search([('as_descontinuado','=',False)])
      filas+=1   
      cont=0   
      for product in productos:
        cont+=1
        sheet.write(filas, 0, cont)
        sheet.write(filas, 1, product.as_codigo_proveedor)
        sheet.write(filas, 2, product.name)
        sheet.write(filas, 3, product.default_code)
        sheet.write(filas, 4, product.as_costo_anterior)
        sheet.write(filas, 5, product.as_costo_proveedor)
        sheet.write(filas, 6, product.as_name_proveedor)
        sheet.write(filas, 7, (product.as_costo_proveedor-product.as_costo_anterior))
        if product.as_costo_anterior == 0.00:
          result=0
        else:
          result= (((product.as_costo_anterior-product.as_costo_proveedor)/product.as_costo_anterior)*100)*1
        sheet.write(filas, 8, round(result,2))
        filas+=1

class as_product_exist_excel(models.AbstractModel):
    _name = 'report.as_generando_webservice.product_exist.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

      #Definiciones generales del archivo, formatos, titulos, hojas de trabajo
      sheet = workbook.add_worksheet('Detalle de Movimientos')
      titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold':True })
      titulo1.height = 20 * 50
      titulo2 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
      titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
      titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
      titulo4 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })

      number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00'})
      number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00'})
      number_right_bold = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
      number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
      number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
      number_right_col.set_locked(False)

      letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
      letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
      letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
      letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
      letter5 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True, 'bold': True})
      letter_locked = letter3
      letter_locked.set_locked(False)

      # Aqui definimos en los anchos de columna
      sheet.set_column('A:A',10, letter1)
      sheet.set_column('B:B',20, letter1)
      sheet.set_column('C:C',30, letter1)
      sheet.set_column('D:D',20, letter1)
      sheet.set_column('E:E',20, letter1)
      sheet.set_column('F:F',20, letter1)

      # titulos
      sheet.merge_range('A1:F1', 'REPORTE DE EXISTENCIAS DE PRODUCTOS', titulo1)
      sheet.set_row(0, 40)
      sheet.write(1, 0, 'Fecha y Hora',titulo3)
      sheet.write(1, 1, datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

      filas=4
      sheet.write(filas, 0, 'N',titulo2)
      sheet.write(filas, 1, 'Codigo Proveedor',titulo2)
      sheet.write(filas, 2, 'Nombre del Producto',titulo2)
      sheet.write(filas, 3, 'Codigo Producto Interno',titulo2)
      sheet.write(filas, 4, 'Existencias',titulo2)
      sheet.write(filas, 5, 'Nombre del Proveedor',titulo2)
      productos = self.env['product.product'].search([('as_descontinuado','=',False)])
      filas+=1   
      cont=0   
      for product in productos:
        cont+=1
        sheet.write(filas, 0, cont)
        sheet.write(filas, 1, product.as_codigo_proveedor)
        sheet.write(filas, 2, product.name)
        sheet.write(filas, 3, product.default_code)
        sheet.write(filas, 4, product.as_existencias)
        sheet.write(filas, 5, product.as_name_proveedor)
        filas+=1

    