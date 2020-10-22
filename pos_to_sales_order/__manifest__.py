# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Home Delivery",
  "summary"              :  "The module allows you to create Sales quotations from running Odoo POS session. The quotations are saved in the Odoo backend and can be processed later manually.",
  "category"             :  "Point of Sale",
  "version"              :  "1.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Home-Delivery.html",
  "description"          :  """Odoo POS Home Delivery
POS create Sales quotation
POS manual order
Take sale order POS
POS manual delivery
POS delivery order""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_to_sales_order",
  "depends"              :  [
                             'point_of_sale',
                             'sale',
                            ],
  "data"                 :  [
                             'views/pos_to_sales_order_view.xml',
                             'views/templates.xml',
                             'data/pos_to_sale_order_demo.xml',
                             'security/ir.model.access.csv',
                            ],
  "qweb"                 :  ['static/src/xml/pos_to_sale_order.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  35,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}