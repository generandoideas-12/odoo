/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_to_sales_order.pos_to_sales_order', function(require) {
    "use strict";
	var rpc = require('web.rpc');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var ActionManager1 = require('web.ActionManager');
    var PopupWidget = require("point_of_sale.popups");
    var gui = require('point_of_sale.gui');
    var _t = core._t;

    var CustomInfoPopup = PopupWidget.extend({
        template: 'CustomInfoPopup',
    });
    gui.define_popup({ name: 'pos_to_sale_order_custom_message', widget: CustomInfoPopup });

    var OrderPrintPopupWidget = PopupWidget.extend({
        template: 'OrderPrintPopupWidget',

        events: _.extend({}, PopupWidget.prototype.events, {
            'click .wk_print_quotation': 'delivery_print_quotation',
            'click .wk_email': 'delivery_send_mail',
        }),
        delivery_print_quotation: function() {
            var self = this;
            var order_id = parseInt($('.wk_print_quotation').attr('id'));
            setTimeout(function(){
                self.chrome.do_action('sale.action_report_saleorder',{additional_context:{ 
                    active_ids:[order_id],
                }})
                 .fail(function(error, event) {
                    self.gui.show_popup('error', {
                        'title': _t("Error!!!"),
                        'body': _t("Check your internet connection and try again."),
                    });
                });
                self.gui.show_screen('products');
            },500)
        },
        delivery_send_mail: function() {
            var self = this;
            var order_id = parseInt($('.wk_print_quotation').attr('id'));
             rpc.query({
                model: 'pos.sales.order',
                method: 'send_email',
                args: [order_id],
            })
            .then(function(result) {
                self.gui.show_popup('pos_to_sale_order_custom_message', {
                    'title': _t('Successful'),
                    'body': _t('Email is sent.'),
                    cancel: function() {
                        self.gui.show_screen('products');
                    },
                });
            })
            .fail(function(error, event) {
                self.gui.show_popup('error', {
                    'title': _t("Error!!!"),
                    'body': _t("Check your internet connection and try again."),
                });
            });
        },
    });
    gui.define_popup({ name: 'orderPrintPopupWidget', widget: OrderPrintPopupWidget });

    var CreateSalesOrderPopupWidget = PopupWidget.extend({
        template: 'CreateSalesOrderPopupWidget',

        events: _.extend({}, PopupWidget.prototype.events, {
            'click .diffrent_address': 'customer_diffrent_address',
            'click .extra_fee': 'delivery_extra_fees',
            'click .wk_create_order': 'create_delivery_sale_order',
        }),
        customer_diffrent_address: function() {
            if ($('.diffrent_address').is(':checked')) {
                $('.wk_address').show();
            } else {
                $('.wk_address').hide();
            }
        },
        delivery_extra_fees: function() {
            var self = this;
            if ($('.extra_fee').is(':checked')) {
                if (self.pos.config.extra_price_product_id[0] != undefined){
                    $('#no_extra_product').hide();
                    $('.extra_fee_value').show();
                } 
                else {
                    $('.extra_fee_value').hide();
                    $(".extra_fee").prop('checked', false);
                    $('#no_extra_product').show();
                }
            } else
                $('.extra_fee_value').hide();
        },
        create_delivery_sale_order: function() {
            var self = this;
            var order = self.pos.get('selectedOrder');
            var note = $('.wk_note').val();
            var exp_date = $('.input_date').val();
            var client_fields = false;
            var client = order.get_client();
            var user = self.pos.cashier || self.pos.user;
            if ($('.extra_fee').is(':checked')) {
                var product = self.pos.db.get_product_by_id(self.pos.config.extra_price_product_id[0]);
                if ($.isNumeric($('.extra_fee_value').val())) {
                    var extra_amout = parseFloat($('.extra_fee_value').val());
                    order.add_product(product, {
                        price: extra_amout
                    });
                }
            }
            var orderdata = order.export_as_JSON();
            var orderLine = order.orderlines;
            if ($('.diffrent_address').is(':checked')) {
                client_fields = self.return_client_details(client.id);
                if (client_fields != false) {
                    self.create_sale_order_rpc([orderdata, note, user.id, client_fields, exp_date]);
                } else {
                    self.pos.gui.show_popup('pos_to_sale_order_custom_message', {
                        'title': _t("Error"),
                        'body': _t("Customer name is required."),
                    });
                }
            } else {
                self.create_sale_order_rpc([orderdata, note, user.id, client_fields, exp_date]);
            }
        },
        create_sale_order_rpc: function(values) {
            var self = this;
             rpc.query({
                model: 'pos.sales.order',
                method: 'create_pos_sale_order',
                args: values,
            })
            .fail(function(unused, event) {
                self.gui.show_popup('error', {
                    'title': _t("Error!!!"),
                    'body': _t("Check your internet connection and try again."),
                });
            })
            .done(function(result) {
                self.pos.delete_current_order();
                self.gui.show_popup('orderPrintPopupWidget', {
                    'title': result.name,
                    'order_id': result.id
                });
            });
        },
        return_client_details: function(partner_id) {
            var self = this;
            var fields = {};
            this.$('.wk_address').each(function(idx, el) {
                fields[el.name] = el.value;
            });
            if (!fields.name) {
                return false;
            }
            fields.id = partner_id || false;
            fields.country_id = fields.country_id || false;
            return fields;
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.wk_address').hide();
            this.$('.extra_fee_value').hide();
        },
    });
    gui.define_popup({ name: 'Create_Sales_Order_popup_widget', widget: CreateSalesOrderPopupWidget });

    var CreateSalesOrderWidget = screens.ActionButtonWidget.extend({
        template: 'CreateSalesOrderWidget',

        button_click: function() {
            var self = this;
            var order = self.pos.get('selectedOrder');
            var client = order.get_client();
            var orderLine = order.orderlines;
            if (orderLine.length == 0) {
                self.pos.gui.show_popup('pos_to_sale_order_custom_message', {
                    'title': _t("Empty Cart!"),
                    'body': _t("There is no product in selected Order."),
                });
            } else if (client == null) {
                self.gui.show_popup('confirm', {
                    'title': _t('Please select the Customer'),
                    'body': _t('You need to select the customer first.'),
                    confirm: function() {
                        self.gui.show_screen('clientlist');
                    },
                });
            } else {
                self.gui.show_popup('Create_Sales_Order_popup_widget', {});
            }
        },
    });
    screens.define_action_button({
        'name': 'SalesOrder',
        'widget': CreateSalesOrderWidget,
        'condition': function() {
            return true;
        },
    });
});
