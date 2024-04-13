# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from urllib import urlencode
from urlparse import urljoin


class CrmTeamExtend(models.Model):
    _inherit = 'crm.team'

    warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse')


    def _get_default_team_id(self, user_id=None):
        res = None
        settings_obj = self.env['sale.config.settings']
        is_select_sales_team  = settings_obj.search([('is_select_sales_team', '=', True)], limit=1)
        if not is_select_sales_team :
            res = super(CrmTeamExtend,self)._get_default_team_id(user_id=user_id)
        return  res

class SaleConfig(models.Model):
    _inherit = 'sale.config.settings'

    is_select_sales_team = fields.Boolean('Users Must Select Sales Channel')


class SaleOrderExtend(models.Model):
    _inherit = "sale.order"


    @api.onchange('team_id')
    def _team_id(self):
        if self.team_id.warehouse_id:
            self.warehouse_id = self.team_id.warehouse_id.id
        else :
            company = self.env.user.company_id.id
            self.warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)


    @api.multi
    def action_view_delivery(self):
        res = super(SaleOrderExtend,self).action_view_delivery()
        res['target'] = 'new'
        return  res


    def _get_url(self, module_name,menu_id,action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name,menu_id)[1]
        fragment['model'] =  'stock.picking'
        fragment['view_type'] = 'form'
        fragment['action']= model_data.get_object_reference(module_name,action_id)[1]
        query = {'db': self.env.cr.dbname}

# for displaying tree view. Remove if you want to display form view
#         fragment['page'] = '0'
#         fragment['limit'] = '80'
#         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


 # For displaying a single record. Remove if you want to display tree view

        fragment['id'] =  context.get("picking_id")
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


        return res

    @api.multi
    def close_alert_box(self):
        self.show_alert_box = False
        return


    @api.multi
    def action_confirm(self):
        res = super(SaleOrderExtend,self).action_confirm()
        picking_id = self.picking_ids[0]

        # Send Email to the Stock Person
        company_email = self.env.user.company_id.email.strip()
        if company_email :
            # Custom Email Template
            mail_template = self.env.ref('kin_sales.mail_templ_delivery_transfer_created')
            ctx = {}
            ctx.update({'picking_id':picking_id.id})
            the_url = self._get_url('stock','all_picking','action_picking_tree_all',ctx)
            users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

            for user in users :
                if user.has_group('kin_sales.group_receive_delivery_stock_transfer_email') and user.partner_id.email.strip() :
                    ctx = {'system_email': company_email,
                            'stock_person_email':user.partner_id.email,
                            'stock_person_name': user.partner_id.name ,
                            'url':the_url,
                            'origin': picking_id.origin
                        }
                    mail_template.with_context(ctx).send_mail(picking_id.id,force_send=False)
                    self.show_alert_box = True
        return res

    show_alert_box  = fields.Boolean(string="Show Alert Box")

    @api.multi
    def action_view_invoice(self):
        res = super(SaleOrderExtend,self).action_view_invoice()
        res['target'] = 'new'
        return  res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.env['product.uom']._compute_qty_obj(self.product_uom, self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    pass
                    # warning_mess = {
                    #     'title': _('Not enough inventory!'),
                    #     'message' : _('You plan to sell %.2f %s but you only have %.2f %s available!\nThe stock on hand is %.2f %s.') % \
                    #         (self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
                    # }
                    #return {'warning': warning_mess}
        return {}




