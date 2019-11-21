# -*- coding: utf-8 -*-
from odoo.tools.translate import _
from odoo import http
from odoo import http
from odoo.http import request
import datetime
from datetime import datetime, date
from pytz import timezone, UTC
from dateutil.tz import tzlocal
# from tabulate import tabulate
import json
import sys
import yaml
import logging
_logger = logging.getLogger(__name__)

from werkzeug import urls
from werkzeug.wsgi import wrap_file

import re

def as_convert(txt,digits=50,is_number=False):
    if is_number:
        num = re.sub("\D", "", txt)
        if num == '':
            return 0
        return int(num[0:digits])
    else:
        return txt[0:digits]


class webservice(http.Controller):
    @http.route('/movilcrm/login', auth='public', type="http", cors='*')
    def user(self, **post):
        as_usuario = post.get('as_usuario') if post.get('as_usuario') else ''
        as_password = post.get('as_password') if post.get('as_password') else ''
        callback = post.get('callback') if post.get('callback') else ''
        if as_usuario and as_password:
            user = request.env['res.users']
            user_exist_ids = user.sudo().search([('as_usuario','=',as_usuario)],limit=1)
            user_ids = user.sudo().search([('as_usuario','=',as_usuario),('as_password','=',as_password)],limit=1)
            if user_exist_ids:
                if user_ids:
                    tz = user.sudo().search([('as_usuario','=',as_usuario)]).tz
                    as_json_user = {"user":[]}

                    rp = {
                            "id": user_ids.id,
                            "login": as_convert(user_ids.login or ""), #Nombre cliente
                            "email": as_convert(user_ids.email  or ""), #Telefono
                            "email": as_convert(user_ids.as_suspendido  or ""), #Telefono
                            "email": as_convert(user_ids.as_url_odoo  or ""), #Telefono
                            }
                    as_json_user["user"].append(rp)      
                    # return "%s(%s)" % (callback,json.dumps(as_json_user))
                    return json.dumps(as_json_user)
                else:
                    return json.dumps({'error': _('Password invalido')})
            else:
                return json.dumps({'error': _('Usuario invalido')})
        else:
            return json.dumps({'error': _('No permitido')})

    @http.route(['/movilcrm/token',], auth="public", type="http", cors='*')
    def token(self, **post):
        """
            Para autenticar se deben enviar usuario y password
            servidor.com:8069/webservice/token?login=admin&password=admin
        """
        res = {}
        try:
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid:
                user = request.env['res.users'].sudo().browse(uid)
                token = user.get_user_access_token()
                user.token = token
                res['token'] = token
                request.session.logout()
            else:
                res['error'] = "Login o Password erroneo"
            return json.dumps(res)
        except:
            res['error'] = "Envia login y password"
            return json.dumps(res)