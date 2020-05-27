# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
import base64
from datetime import datetime,date
from odoo.tools import ustr
from io import StringIO
import io

try:
    import xlwt
except ImportError:
    xlwt = None

class transport(models.Model):

    _name = 'transport'

    name = fields.Char('Name')
    contact_name = fields.Char('Contact Name')
    street = fields.Char('street')
    street2 = fields.Char('street2')
    phone = fields.Char('Phone')
    vehicle_id =  fields.Many2one('fleet.vehicle', 'Transport Vehicle')
    comment = fields.Text('Comment')
    image =  fields.Binary('Transporters Image')
    imgsm = fields.Binary("Image of transport", attachment=True)
    image_medium = fields.Binary("Image", attachment=True)

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(transport, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(transport, self).write(vals)

class transport_location_details(models.Model):

    _name = 'transport.location.details'

    source_loc = fields.Many2one('route.locations', 'Source Location')
    dest_loc  = fields.Many2one('route.locations','Destination Location')
    distance = fields.Float('Distance (KM)')
    time   = fields.Float('Time in Hours')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    note  = fields.Char('Comment')
    tracking_number  =  fields.Char('Tracking Number')
    picking_id = fields.Many2one('stock.picking')
    transport_entry_id = fields.Many2one('transport.entry')
    route_id = fields.Many2one('transport.route', 'Route Of Transportation')
    state = fields.Selection([('draft', 'Draft'), ('waiting','Waiting'), ('done', 'Done')] , 'State')

class transport_location(models.Model):
    _name  = 'route.locations'

    name =  fields.Char('Location Name')

class transport_route(models.Model):
    _name  = 'transport.route'

    name = fields.Char('Name')
    transporter_id  = fields.Many2one('transport','Transporter')
    rote_locations_ids  =  fields.One2many('transport.location.details', 'route_id', 'Route Lines')
    
class transport_entry(models.Model):
    _name = "transport.entry"
    _rec_name = 'contact_person' 

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('trnsport.entry') or _('New')
        return super(transport_entry, self).create(vals)
                 
    @api.one       
    def move_to_halt(self):             
        self.state = 'waiting'       

    @api.one       
    def move_to_done(self):             
        self.state = 'done'

    @api.one       
    def move_to_cancel(self):             
        self.state = 'cancel'

    @api.one       
    def copy_transport_entry(self):             
        res = {}
        if self.state =='cancel':
           new_record = self.env['transport.entry'].create({'picking_id':self.picking_id.id,
                                                'transport_id':self.transport_id.id,
                                               'date': date.today(),
                                              'lr_number':'',
                                              'no_of_parcels':self.no_of_parcels,
                                              'contact_person': self.contact_person,
                                              'state':'draft' , 
                                              'active': True,
                                              'customer_id':self.customer_id.id })

           self.unlink()
           res = {
                      'view_mode': 'form',
                      'res_id': new_record.id,
                      'res_model': 'transport.entry',
                      'view_type': 'form',
                      'type': 'ir.actions.act_window',
              }
           return res

    name =  fields.Char('Name')
    date = fields.Date('Transport Date')
    note = fields.Text('Note')
    active = fields.Boolean('Active')
    picking_id = fields.Many2one('stock.picking', string="Delivery Order")
    customer_id = fields.Many2one('res.partner', 'Customer')
    contact_person = fields.Char('Contact Name')
    no_of_parcels = fields.Integer('No Of Parcels')
    lr_number = fields.Char('LR Number')
    vehicle_id =  fields.Many2one('fleet.vehicle', 'Transport Vehicle')
    state =  fields.Selection([('draft', 'Start'),('waiting','Waiting'),('done','Done'),('cancel','Cancel'),
                                  ], default =  'draft', copy = False)        
    transport_id = fields.Many2one('transport', 'Transport Name')
    transport_rote_ids  = fields.One2many('transport.location.details', 'transport_entry_id')
      
class stock_picking(models.Model):
    _inherit = 'stock.picking'

    transport_id  =  fields.Many2one('transport')
    no_of_parcels = fields.Integer('No Of Parcels')
    lr_number =  fields.Integer('LR Number')
    parcel_entry_done =  fields.Boolean('Parcel Entry Done', default = False, copy=False)
    transport_ids = fields.One2many('transport.entry', 'picking_id','Transport Entries')
    trans_ids = fields.One2many('transport.entry', 'picking_id')
    route_id  = fields.Many2one('transport.route', 'Route')
    transport_routes_ids = fields.One2many('transport.location.details','picking_id')
    trans_count = fields.Integer(string='Number of Transport Entry',compute='_get_products_count')

    @api.one
    @api.depends('trans_ids')
    def _get_products_count(self):
        self.trans_count = len(self.trans_ids)

    @api.onchange('route_id')
    def onchange_route_id(self):
        lines = [] 
        origin  = self.origin
        sale_orders = self.env['sale.order'].search([('name', '=', origin)])

        picking = self       
        for location in self.route_id.rote_locations_ids:
            abc = {
                'source_loc':location.source_loc.id, 
                'picking_id': self.id,        
                'dest_loc':location.dest_loc.id, 
                'distance':location.distance,
                'time':location.time 
            }
            if picking:
                res= self.env['transport.location.details'].create({
                    'source_loc':location.source_loc.id, 
                    'picking_id': picking.id,        
                    'dest_loc':location.dest_loc.id, 
                    'distance':location.distance,
                    'time':location.time 
                })
            lines.append(res.id)
        self.transport_routes_ids  = [(6,0,lines)]  

class account_invoices_report_excel(models.TransientModel):
    _name = "daily.taransport.report.excel"
    
    excel_file = fields.Binary('Excel Report for Daily Transport')
    file_name = fields.Char('Excel File', size=64)

class transport_entry_report_wizard(models.TransientModel):
    _name = "transport.entry.wizard"
    
    start_date = fields.Date('Date')
    trasporter_id  =  fields.Many2one('transport', 'Select Transporter')
    
    @api.multi
    def print_excel_report(self):
        res={}
        object_of_transport_entry = self.env['transport.entry']
        
        date  = str(self.start_date)
        transport_id  = self.trasporter_id.name
        vehicle_name = self.trasporter_id.vehicle_id.name

        company_name = self.env['res.users'].browse(self.env.uid).company_id.name
        
        company_address = self.env['res.users'].browse(self.env.uid).company_id.street or  '' + "," + self.env['res.users'].browse(self.env.uid).company_id.street2 or  ''
        company_city =  self.env['res.users'].browse(self.env.uid).company_id.city
        company_state =  self.env['res.users'].browse(self.env.uid).company_id.state_id.name
        company_country = self.env['res.users'].browse(self.env.uid).company_id.country_id.name

        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        style2 = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') 

        # Create a font to use with the style
        font = xlwt.Font()
        font.name = 'calibri'
        font.bold = True
        font.height = 200
        style.font = font
        index = 1

        #simple font
        font2 = xlwt.Font()
        font2.name = 'Bitstream Charter'
        font2.bold = False
        font2.height = 200
        style2.font = font2
        index = 1

        #company Address
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write(0, 0, company_name , style)
        #worksheet.write(1, 0, company_address , style)
        worksheet.write(2, 0, company_city , style)
        worksheet.write(3, 0, company_state , style)
        worksheet.write(4, 0, company_country , style)

        #transporter and date start deatils
        
        worksheet.write(7, 0, 'Transporter' , style)
        worksheet.write(7, 1,  transport_id, style2)  
        
        worksheet.write(8, 0, 'Vehicle' , style)
        worksheet.write(8, 1,  vehicle_name, style2)  
 
        worksheet.write(7, 4, 'Date' , style)
        worksheet.write(7, 5, date  , style2) 

        if self.trasporter_id.id and self.start_date:
            self._cr.execute('select * from transport_entry where (transport_id =%s) and date = (%s) and active = True', (self.trasporter_id.id, self.start_date, ))

            records = self._cr.dictfetchall()
            sr_no  = 1
            findal_list_of_data  = []

            worksheet.write(10, 0, 'Order #', style)
            worksheet.write(10, 1, 'Customer', style)
            worksheet.write(10, 2, 'Customer Address', style)
            worksheet.write(10, 3, 'Delivery No', style)
            worksheet.write(10, 4, 'No of Parcel', style)
            worksheet.write(10, 5, 'Lr No', style)
            worksheet.write(10, 6, 'Check', style)
            worksheet.write(10, 7, 'Obs', style)
     
            for rec in records:
                if    self.env['stock.picking'].browse(rec['picking_id']).partner_id.street != False and  self.env['stock.picking'].browse(rec['picking_id']).partner_id.street2 != False:
                    partner_address = str(self.env['stock.picking'].browse(rec['picking_id']).partner_id.street)  + ","+ str(self.env['stock.picking'].browse(rec['picking_id']).partner_id.street2) or  ''
                elif self.env['stock.picking'].browse(rec['picking_id']).partner_id.street == False and  self.env['stock.picking'].browse(rec['picking_id']).partner_id.street2 != False: 
                    partner_address = str(self.env['stock.picking'].browse(rec['picking_id']).partner_id.street2) or  ''
                elif self.env['stock.picking'].browse(rec['picking_id']).partner_id.street != False and  self.env['stock.picking'].browse(rec['picking_id']).partner_id.street2 == False: 
                    partner_address = str(self.env['stock.picking'].browse(rec['picking_id']).partner_id.street) or  ''
                elif self.env['stock.picking'].browse(rec['picking_id']).partner_id.street == False and  self.env['stock.picking'].browse(rec['picking_id']).partner_id.street2 == False: 
                    partner_address = ''
  
                data_dict  =  {'order_no' : sr_no ,
                           'customer_id': self.env['res.partner'].browse(rec['customer_id']).name,
                            'Address':partner_address,
                            'picking_number': self.env['stock.picking'].browse(rec['picking_id']).name,
                            'no_of_parcel':self.env['stock.picking'].browse(rec['picking_id']).no_of_parcels,
                            'status':rec['state'],
                            'note':rec['note'],
                            'lr_no': self.env['stock.picking'].browse(rec['picking_id']).lr_number,
                            }    

                sr_no =  sr_no + 1
                findal_list_of_data.append(data_dict)   
        
            #heading 
            row  = 11
            for vals in findal_list_of_data:
                worksheet.write(row, 0, ustr(vals['order_no']))
                worksheet.write(row, 1, ustr(vals['customer_id']))
                if vals['Address'] == str(False):
                   vals['Address'] = ''
                worksheet.write(row, 2, ustr(vals['Address']))
                worksheet.write(row, 3, ustr(vals['picking_number']))
                worksheet.write(row, 4, ustr(vals['no_of_parcel']))
                worksheet.write(row, 5,ustr(vals['lr_no']))
                worksheet.write(row, 6,ustr(vals['status']))
                worksheet.write(row, 7,ustr(vals['note'])) 
        
                row = row + 1 

                filename = 'Transport_Daily_Report.xls'        
                fp = io.BytesIO()
                workbook.save(fp)
                export_id = self.env['daily.taransport.report.excel'].create( {'excel_file': base64.encodestring(fp.getvalue()),'file_name': filename})
        
                res = {
                        'view_mode': 'form',
                        'res_id': export_id.id,
                        'res_model': 'daily.taransport.report.excel',
                        'view_type': 'form',
                        'type': 'ir.actions.act_window',
                        'target':'new'
                }
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
