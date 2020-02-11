/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_change_logo.pos_change_logo', function (require) {
	"use strict";
	var _t = require('web.core')._t;
	var chrome = require('point_of_sale.chrome');
	
	chrome.Chrome.include({
		get_logo: function(){
			var self = this;
			var img = new Image();
			img.onload = function() {
				var ratio = 1;
				var targetwidth = 300;
				var maxheight = 150;
				if( img.width !== targetwidth ){
					ratio = targetwidth / img.width;
				}
				if( img.height * ratio > maxheight ){
					ratio = maxheight / img.height;
				}
				var width  = Math.floor(img.width * ratio);
				var height = Math.floor(img.height * ratio);
				var c = document.createElement('canvas');
					c.width  = width;
					c.height = height;
				var ctx = c.getContext('2d');
					ctx.drawImage(img,0,0, width, height);
				self.pos_logo_base_64 = c.toDataURL();
			};
			img.src = window.location.origin + '/web/binary/image?model=pos.config&field=pos_logo&id='+self.pos.config.id;
			return window.location.origin + '/web/binary/image?model=pos.config&field=pos_logo&id='+this.pos.config.id
		},
	});
});