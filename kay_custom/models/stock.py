from openerp import models, fields,api
from datetime import datetime
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from urllib import urlencode
from urlparse import urljoin



class StockExtend(models.Model):
    _inherit = 'stock.picking'

    store_approval_time_start = fields.Datetime(string="Store Time Start",default=fields.datetime.now(),readonly=True)
    store_approval_time_end = fields.Datetime(string="Store Time End",readonly=True)
    store_approval_done = fields.Boolean(string="Store Approved",default=False)
    purchase_draft_po_time_start = fields.Datetime(string="Draft POS time Start",readonly=True)
    purchase_draft_po_time_end = fields.Datetime(string="Draft PO tiem end",readonly=True)
    purchase_draft_po_approval_done = fields.Boolean(string="Draft PO done")
    reciever_signature = fields.Binary(string="Receivers Signature",readonly=False, states={'done': [('readonly',False)]})
    del_signature = fields.One2many('delivery.signature','id',string="Delivery Signature")
    sent = fields.Boolean(default=False)

    @api.multi
    def write(self, vals):
        res = super(StockExtend, self).write(vals)
        if self.reciever_signature and self.sent == False:
            self.sent = True
            company_email = self.env.user.company_id.email.strip()
            mail_template = self.env.ref('kay_custom.mail_template_delivery_email')
            group_obj = self.env.ref('kin_stock.group_receive_stock_picking_delivered_email')
            if group_obj:
                for user in group_obj.users:
                     if user.partner_id.email and user.partner_id.email.strip():
                         ctx = {'system_email': company_email,
                                          'origin':self.name,                                         
                                            'saleperson':'Operation Manager',
                                           'hr_email':user.partner_id.email,
                                           'url':'',
                                           }
                         mail_template.with_context(ctx).send_mail(self.id,force_send=False)

        return res



    @api.multi
    def store_approval_done_action(self):
        for rec in self:
            rec.store_approval_done = True
            rec.store_approval_time_end = fields.datetime.now()


    @api.model
    def store_approval_timeout(self):
        stock_pick_obj = self.env['stock.picking'].search([('create_date','>',self.env.user.company_id.x_time_start),('state','in',['waiting'])])
        #sales_order_ids = self.pool.get('sale.order').search(cr, uid, [])
      

        for order in stock_pick_obj:
            time_difference = 0

            if not order.store_approval_time_end and order.store_approval_time_start and not order.store_approval_done:
                 d1=datetime.strptime(str(fields.datetime.now()),'%Y-%m-%d %H:%M:%S.%f') 
                 d2=datetime.strptime(str(order.store_approval_time_start),'%Y-%m-%d %H:%M:%S')
                 time_difference = d1 - d2
                 print(time_difference.total_seconds()/60)
                 if float(str(time_difference.total_seconds()/60)) >  15.0:
                     order.update({'store_approval_time_end':datetime.now()})
                     ctx = {}
                     #ctx.update({'sale_id':order.id})
                     #quote_url = order._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

                     #notify HR Manager
                     if not order.store_approval_done and order.store_approval_time_end:
                         history_obj = self.env['timeout.history']
                         history_obj.create({'name':'Delivery Order Timeout','user_id':'Store Manager','document_id':order.name,'time_start':order.store_approval_time_start,'time_end':order.store_approval_time_end,'time_range':'15 minutes'})
                         message_obj = self.env['mail.message']
                         company_email = self.env.user.company_id.email.strip()
                         mail_template = self.env.ref('kay_custom.mail_template_send_to_store')

                         group_obj = self.env.ref('base.group_hr_manager')
                         if group_obj:
                             for user in group_obj.users:
                                 if user.partner_id.email and user.partner_id.email.strip():

                                     ctx = {'system_email': company_email,
                                           'origin':order.name ,
                                           'saleperson':'Store Manager',
                                           'hr_email':user.partner_id.email,
                                           'url':'',
                                           }
                                     mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                        

	    elif not order.purchase_draft_po_time_end and order.purchase_draft_po_time_start and not order.purchase_draft_po_approval_done:
           
                 d1=datetime.strptime(str(fields.datetime.now()),'%Y-%m-%d %H:%M:%S.%f') 
                 d2=datetime.strptime(str(order.purchase_draft_po_time_start),'%Y-%m-%d %H:%M:%S')
                 time_difference = d1 - d2
                 print(time_difference.total_seconds()/60)
                 if float(str(time_difference.total_seconds()/60)) >  15.0:
                     order.update({'purchase_draft_po_time_end':datetime.now()})
                     ctx = {}
                     #ctx.update({'sale_id':order.id})
                     #quote_url = order._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

                     #notify HR Manager
                     if not order.purchase_draft_po_approval_done and order.purchase_draft_po_time_end:
                         history_obj = self.env['timeout.history']
                         history_obj.create({'name':'Draft Purchase order Timeout','user_id':'Purchase manager','document_id':order.name,'time_start':order.purchase_draft_po_time_start,'time_end':order.purchase_draft_po_time_end})
                         message_obj = self.env['mail.message']
                         company_email = self.env.user.company_id.email.strip()
                         mail_template = self.env.ref('kay_custom.mail_template_send_todraft_po')

                         group_obj = self.env.ref('base.group_hr_manager')
                         if group_obj:
                             for user in group_obj.users:
                                 if user.partner_id.email and user.partner_id.email.strip():
                                     #user_ids.append(user.id)


                                     ctx = {'system_email': company_email,
                                            'origin':order.name ,
                                            'saleperson':'Store Manager',
                                            'hr_email':user.partner_id.email,
                                            'url':'',
                                         }
                                     mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                         print("Draft PO Timeout")
	

    def action_assign(self, cr, uid, ids, context=None):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state == 'draft':
                self.action_confirm(cr, uid, [pick.id], context=context)
            #skip the moves that don't need to be checked
            move_ids = [x.id for x in pick.move_lines if x.state not in ('draft', 'cancel', 'done')]
            if not move_ids:
                raise UserError(_('Nothing to check the availability for.'))
            self.pool.get('stock.move').action_assign(cr, uid, move_ids, context=context)
	    pick.store_approval_done = True
	    pick.purchase_draft_po_time_start = fields.datetime.now()
        return True
    



class SignatureModel(models.Model):
    _name = "delivery.signature"


    reciever_signature = fields.Binary(string="Receivers Signature",readonly=False, states={'done': [('readonly',False)]})
    recieved_date = fields.Datetime(string="Recieving Date")
    recievers_name = fields.Char(string="Recievers Name")
    stock_picking_id_s = fields.Many2one('stock.picking',string="Stock picking",ondelete='cascade')

