# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AhorasoftProductos(models.TransientModel):
    _name = "as.product.report.descontinuado"
    _description = "Productos descontinuados de AhoraSoft"


    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.product.report.descontinuado'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_generando_webservice.as_product_report_fisico').report_action(self, data=datas)

class AhorasoftProductos(models.TransientModel):
    _name = "as.product.report.price"
    _description = "Productos descontinuados de AhoraSoft"


    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.product.report.price'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_generando_webservice.as_product_report_price').report_action(self, data=datas)

class AhorasoftProductos(models.TransientModel):
    _name = "as.product.report.exist"
    _description = "Productos descontinuados de AhoraSoft"


    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.product.report.exist'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_generando_webservice.as_product_report_exist').report_action(self, data=datas)