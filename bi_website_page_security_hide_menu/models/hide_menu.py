from odoo import api, fields, models,_


class InheritWebsite(models.Model):
    _inherit="website"

    def hide_menu(self):
        return True

class HideUserMenus(models.Model):
    _name = "hide.website_menus"
    _description="hide website menus" 

    name = fields.Char(string="Name", readonly=1)

    user_type = fields.Char(string="user type")
    #menus
    internal_user=fields.Many2many("website.menu",string="Internal user menus")
    #pages
    page_internal_user=fields.Many2many("website.page",string="Internal users page")
    
    

class InheritMenu(models.Model):
    _inherit = "website.menu"

    hide_website=fields.Many2one("hide.website_menus")
    # is_visible = fields.Boolean(compute='_compute_visible',string='Is Visible')
    visible=fields.Boolean(string="visible")
    hide_user =fields.Many2many('res.users')
    hide_groups = fields.Many2many('res.groups')

    def hide_menus(self):
        hide_list=[]
        user_id = self.env.user
        if user_id.has_group('base.group_user'):
            search_result = self.env['hide.website_menus'].search([('user_type','=','internal')])
            for menu in search_result.internal_user:
                hide_list.append(menu.id)
        # return hide_list

        if user_id.has_group('base.group_portal'):
            search_result = self.env['hide.website_menus'].sudo().search([('user_type','=','portal')])
            for menu in search_result.internal_user:
                hide_list.append(menu.id)

        if user_id.has_group('base.group_public'):
            search_result = self.env['hide.website_menus'].sudo().search([('user_type','=','public')])
            for menu in search_result.internal_user:
                hide_list.append(menu.id)

        if user_id.menus_user:
            for menu in user_id.menus_user:
                hide_list.append(menu.id)


        group_name=self.env['res.groups'].sudo().search([])
        for group in group_name:
            if group.menus_user:
                for user in group.users:
                    if user.id == user_id.id:
                        for menu in group.menus_user:
                            hide_list.append(menu.id)

        if self.hide_user:
            for user in self.hide_user:
                if user.id == user_id.id:
                    hide_list.append(self.id)


        if self.hide_groups:
            for group in self.hide_groups:
                for user in group.sudo().users:
                    if user.id == user_id.id:
                        hide_list.append(self.id)

        return hide_list


    def specific_user(self):
        hide_list=[]
        search_result = self.env.user
        for menu in search_result.menus_user:
            hide_list.append(menu.id)
        return hide_list

class InheritPage(models.Model):
    _inherit = "website.page"

    visible=fields.Boolean(string="visible")

class InheritUsers(models.Model):
    _inherit = "res.users"

    #menus
    menus_user=fields.Many2many("website.menu",string="Internal user menus")
    #pages
    page_user=fields.Many2many("website.page",string="Internal users page")


class InheritGroups(models.Model):
    _inherit = "res.groups"

    #menus
    menus_user=fields.Many2many("website.menu",string="Internal user menus")
    #pages
    page_user=fields.Many2many("website.page",string="Internal users page")




    