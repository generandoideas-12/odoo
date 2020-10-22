# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from odoo import models, api
from odoo.http import request


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def insert_attachment(self, model, id_record, files, filename):
        attachment_obj = self.env['ir.attachment']
        # if asuffix is required add to this dict the input name and
        # the suffix to add to the file name
        suffixes = {
            'purchase_order': 'PO',
            'receipt': 'AC',
        }
        for fname, xml_file in files.items():
            if fname == 'pdf' or fname == 'xml':
                if not xml_file:
                    continue
                suffix = suffixes.get(fname, '')
                new_name = filename if not suffix else '%s_%s' % (filename, suffix)
                attachment_value = {
                    'name': '%s.%s' % (new_name, xml_file.mimetype.split('/')[1]),
                    # 'name': xml_file.filename,
                    'datas': base64.b64encode(xml_file.read()),
                    'datas_fname': xml_file.filename,
                    'res_model': model,
                    'res_id': id_record,
                }
                attachment_obj += attachment_obj.create(attachment_value)
            # else:
            #     uploaded_files = request.httprequest.files.getlist(files['purchase_order'])
            #     for file in uploaded_files:
            #         # print(file.read())
            #         if not file:
            #             continue
            #         suffix = suffixes.get(fname, '')
            #         new_name = filename if not suffix else '%s_%s' % (filename, suffix)
            #         attachment_value = {
            #             # 'name': '%s.%s' % (new_name, file.mimetype.split('/')[1]),
            #             'name': file.filename,
            #             'datas': base64.b64encode(file.read()),
            #             'datas_fname': file.filename,
            #             'res_model': model,
            #             'res_id': id_record,
            #         }
            #         attachment_obj += attachment_obj.create(attachment_value)
        return attachment_obj
