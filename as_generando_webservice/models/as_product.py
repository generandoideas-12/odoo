# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class as_ProductTemplate(models.Model):
	_inherit = 'product.template'


	as_codigo_proveedor = fields.Char(string="Codigo Proveedor")
	as_name_proveedor = fields.Char(string="Nombre Proveedor")
	as_costo_proveedor = fields.Float(string="Costo Proveedor", default=0)
	as_costo_anterior = fields.Float(string="Costo Anterior", default=0)
	as_existencias = fields.Float(string="Existencia Proveedor", default=0)
	as_factor = fields.Float('Factor Precio', default=1)
	as_descontinuado = fields.Boolean('Descontinuado', default=True)

	@api.depends('as_costo_anterior')
	def _calcula_total(self):
		for product in self:
			product.as_price = product.as_costo_proveedor-product.as_costo_anterior
			if product.as_costo_anterior == 0.00:
				result=0
			else:
				result= (((product.as_costo_anterior-product.as_costo_proveedor)/product.as_costo_anterior)*100)*1
				product.as_porcentaje=round(result,2)

	as_price = fields.Float(string="MXN", compute='_calcula_total', store=True)
	as_porcentaje = fields.Float(string="Porcentaje", compute='_calcula_total', store=True)



	