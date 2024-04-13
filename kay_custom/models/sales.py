from openerp import models, fields,api
from datetime import datetime
import openerp.addons.decimal_precision as dp


class SalesExtend(models.Model):
    _inherit = 'sale.order'


    vertical_manager_time_start = fields.Datetime(string="Vertical Manager Time Start", default=lambda self: fields.datetime.now(),readonly=True)
    vertical_manager_time_end = fields.Datetime(string="Vertical Manager Time End",readonly=True)
    vertical_manager_approve = fields.Boolean(string="Approved?",default=False)
    vertical_manager_notification_send = fields.Boolean(String="Notified HR?",default=False)
    sales_order_conversion_time_start = fields.Datetime(string="Sales order Conversion Tme Start",readonly=True)
    sales_order_conversion_time_end = fields.Datetime(string="Sales Order Conversion Time End",readonly=True)
    sales_order_conversion_done = fields.Datetime(string="Quotation Conversion")
    sales_order_approval_time_start = fields.Datetime(string="Sales Order Approval Time Start",readonly=True)
    sales_order_approval_time_end = fields.Datetime(string="Sales Order Apporval Time End",readonly=True)
    sales_order_approval_done = fields.Boolean(string="Sales order Approved?",default=False)
    freight_and_log = fields.Char(string="Freight and Logistics")
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)],'so_to_approve': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quote Sent'),
        ('to_accept', 'Quote Awaiting Acceptance'),
        ('waiting', 'Quote Awaiting Conversion to SO'),
        ('so_to_approve', 'Sale Order To Approve'),
        ('sale', 'Sale Order Approved'),
        ('no_sale', 'On Hold'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


    @api.model
    def vertical_approval_timeout(self):
	print('sales cron starts now')
	sales_order_obj = self.env['sale.order'].search([('create_date','>',self.env.user.company_id.x_time_start)])
  	#sales_order_ids = self.pool.get('sale.order').search(cr, uid, [])
       

        for order in sales_order_obj:
	    time_difference = 0
            #print(order.create_date)
           
            if not order.vertical_manager_time_end and order.vertical_manager_time_start and not order.vertical_manager_approve:
		 d1=datetime.strptime(str(fields.datetime.now()),'%Y-%m-%d %H:%M:%S.%f') 
                 d2=datetime.strptime(str(order.vertical_manager_time_start),'%Y-%m-%d %H:%M:%S')
        	 time_difference = d1 - d2
		 print(time_difference.total_seconds()/60)
		 if float(str(time_difference.total_seconds()/60)) >  15.0:
	             order.update({'vertical_manager_time_end':datetime.now()})
		     ctx = {}
                     ctx.update({'sale_id':order.id})
                     quote_url = order._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

		     #notify HR Manager
		     if not order.vertical_manager_approve and order.vertical_manager_time_end:
			 history_obj = self.env['timeout.history']
			 #history_obj.create({'name':'Quotation Preview Timeout','user_id':order.user_id.name,'document_id':order.name,'time_start':order.vertical_manager_time_start,'time_end':order.vertical_manager_time_end})
                         if history_obj:
                            print("Sent")

		         message_obj = self.env['mail.message']
		         company_email = self.env.user.company_id.email.strip()
			 mail_template = self.env.ref('kay_custom.mail_template_send_to_verticals')
                         group_obj = self.env.ref('base.group_hr_manager')
			 if group_obj:
                             for user in group_obj.users:
                                 if user.partner_id.email and user.partner_id.email.strip():
                                     
                                     ctx = {'system_email': company_email,
                                            'origin':order.quote_name ,
                              		    'saleperson':order.user_id.name,
                                            'hr_email':user.partner_id.email,
                                             'url':quote_url,
                                        }
		                     #mail_template.with_context(ctx).send_mail(self.id,force_send=False)
   			

 
	    #quotation conversion to sales order timeout after approval by the vertical managers
            elif not order.sales_order_conversion_time_end and order.sales_order_conversion_time_start and not order.sales_order_conversion_done:
		 d1=datetime.strptime(str(fields.datetime.now()),'%Y-%m-%d %H:%M:%S.%f') 
                 d2=datetime.strptime(str(order.sales_order_conversion_time_start),'%Y-%m-%d %H:%M:%S')
                 time_difference = d1 - d2
                 print(time_difference.total_seconds()/60)
                 if float(str(time_difference.total_seconds()/60)) >  15.0:
                     order.update({'sales_order_conversion_time_end':datetime.now()})
                     ctx = {}
                     ctx.update({'sale_id':order.id})
                     quote_url = order._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

                     #notify HR Manager
                     if not order.sales_order_conversion_done and order.sales_order_conversion_time_end:
                         history_obj = self.env['timeout.history']
                         history_obj.create({'name':'Quotation Conversion Timeout','user_id':'Sales manager','document_id':order.name,'time_start':order.sales_order_conversion_time_start,'time_end':
			 	order.sales_order_conversion_time_end,'time_range':'10 minutes'})
                         message_obj = self.env['mail.message']
                         company_email = self.env.user.company_id.email.strip()
                         mail_template = self.env.ref('kay_custom.mail_template_quotation_conversion')


                         group_obj = self.env.ref('base.group_hr_manager')
			 if group_obj:
                             for user in group_obj.users:
                                 if user.partner_id.email and user.partner_id.email.strip():

                                     ctx = {'system_email': company_email,
                                           'origin':order.quote_name ,
                                           'saleperson':order.user_id.name,
                                           'hr_email':user.partner_id.email,
                                           'url':quote_url,
                                       }
                                     #mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                         print("Sales Order Conversion Timeout")



	    #check for finance sales order preview
            elif not order.sales_order_approval_time_end and order.sales_order_approval_time_start and not order.sales_order_approval_done:
    	         d1=datetime.strptime(str(fields.datetime.now()),'%Y-%m-%d %H:%M:%S.%f') 
                 d2=datetime.strptime(str(order.sales_order_approval_time_start),'%Y-%m-%d %H:%M:%S')
                 time_difference = d1 - d2
                
                 if float(str(time_difference.total_seconds()/60)) >  15.0:
                     order.update({'sales_order_approval_time_end':datetime.now()})
                     ctx = {}
                     ctx.update({'sale_id':order.id})
                     quote_url = order._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

                     #notify HR Manager
                     if not order.sales_order_approval_done and order.sales_order_approval_time_end:
                         history_obj = self.env['timeout.history']
                         history_obj.create({'name':'Sales Order Approval Timeout Finance','user_id':'Finance','document_id':order.name,'time_start':order.sales_order_approval_time_start,'time_end':order.sales_order_approval_time_end,'time_range':'15 minutes'})
                         message_obj = self.env['mail.message']
                         company_email = self.env.user.company_id.email.strip()
                         mail_template = self.env.ref('kay_custom.mail_template_send_to_SO_approval')

                         group_obj = self.env.ref('base.group_hr_manager')
                         if group_obj:
                              for user in group_obj.users:
                                  if user.partner_id.email and user.partner_id.email.strip():
                                      #user_ids.append(user.id)
 

                                      ctx = {'system_email': company_email,
                                           'origin':order.name ,
                                           'saleperson':order.user_id.name,
                                           'hr_email':order.user_id.email,
                                           'url':quote_url,
                                           }
                                      mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                         



        # sedif not or.vertical_manager_time_end and order.vertical_manager_time_start and not order.vertical_manager_appr
        #message_obj = self.env['mail.message']




    #change quotaton to a 'to approve' state and also send notification to accounting for approval 
    @api.multi
    def action_confirm(self):
        self.state = 'so_to_approve'
        self.confirmed_by_user_id = self.env.user
	self.sales_order_approval_time_start = datetime.now()

        # Give a SO ID
        if self.so_name:
            self.name = self.so_name
        else:
            self.quote_name = self.name
            self.name = self.env['ir.sequence'].get('so_id_code')
            self.so_name = self.name

        #Send FYI email notification
        company_email = self.env.user.company_id.email.strip()
        confirm_person_email = self.confirmed_by_user_id.partner_id.email.strip()
        confirm_person_name = self.confirmed_by_user_id.partner_id.name

        if company_email and  confirm_person_email :
            # Custom Email Template
            mail_template = self.env.ref('kin_sales_double_validation.mail_templ_quote_confirmed')
            ctx = {}
            ctx.update({'sale_id':self.id})
            the_url = self._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

            user_ids = []
            group_obj = self.env.ref('kin_sales_double_validation.group_receive_quotation_confirmed_email')
            for user in group_obj.users:
                if user.partner_id.email and user.partner_id.email.strip():
                    user_ids.append(user.id)
                    ctx = {
                            'system_email': company_email,
                            'confirm_person_name': confirm_person_name ,
                            'confirm_person_email' :confirm_person_email,
                            'notify_person_email': user.partner_id.email,
                            'notify_person_name': user.partner_id.name,
                            'url':the_url
                            }
                    mail_template.with_context(ctx).send_mail(self.id, force_send=False)
            if user_ids:
                self.message_subscribe_users(user_ids=user_ids)
                

            #Send email for approval or disapproval
            mail_template = self.env.ref('kin_sales_double_validation.mail_templ_quote_confirmed_to_approve')
            user_ids = []
            group_obj = self.env.ref('kin_sales_double_validation.group_receive_quotation_confirmed_email_to_approve')
            for user in group_obj.users:
                if user.partner_id.email and user.partner_id.email.strip():
                    user_ids.append(user.id)
                    ctx = {
                        'system_email': company_email,
                        'confirm_person_name': confirm_person_name,
                        'confirm_person_email': confirm_person_email,
                        'notify_person_email': user.partner_id.email,
                        'notify_person_name': user.partner_id.name,
                        'url': the_url
                    }
                    mail_template.with_context(ctx).send_mail(self.id, force_send=False)
            if user_ids :
                self.message_subscribe_users(user_ids=user_ids)

        return


    #finance approval action


    #finance disapproval action
    @api.multi
    def action_disapprove(self,msg):
        reason_for_dispproval = msg
        self.disapproved_by_user_id = self.env.user
        self.state = 'no_sale'
	self.sales_order_approval_done = True


        # Send Email
        company_email = self.env.user.company_id.email.strip()
        disapprove_person_email = self.disapproved_by_user_id.partner_id.email.strip()
        disapprove_person_name = self.disapproved_by_user_id.name

        if company_email and disapprove_person_email:
            # Custom Email Template
            mail_template = self.env.ref('kay_custom.mail_templ_sale_hold')
            ctx = {}
            ctx.update({'sale_id': self.id})
            the_url = self._get_sale_order_url('sale', 'menu_sale_order', 'action_orders', ctx)

            user_ids = []
            group_obj = self.env.ref('kin_sales_double_validation.group_receive_disapprove_sale_order_email')
            for user in group_obj.users:
                if user.partner_id.email and user.partner_id.email.strip():
                    user_ids.append(user.id)
                    ctx = {'system_email': company_email,
                           'disapprove_person_name': disapprove_person_name,
                           'disapprove_person_email': disapprove_person_email,
                           'notify_person_email': user.partner_id.email,
                           'notify_person_name': user.partner_id.name,
                           'url': the_url,
                           'reason_for_dispproval': reason_for_dispproval,
                           }
                    mail_template.with_context(ctx).send_mail(self.id, force_send=False)

            if user_ids :
                self.message_subscribe_users(user_ids=user_ids)
                # For Similar Odoo Kind of Email. Works fine
                #self.message_post( _("Sales Order has been Disapproved with reason: " + reason_for_dispproval + "") ,subject='Please See the Disapproved Sales Order', subtype='mail.mt_comment')

                #Just Log the Note Only
                #self.message_post(_("Sales Order has been Disapproved with reason: " + reason_for_dispproval + ""), subject='Please See the Disapproved Sales Order')
    

    @api.multi
    def action_revert(self):
        for order in self:
	    order.state = 'so_to_approve'


    @api.multi
    def action_order_disapprove(self):
	 self.env['sale.order.disapprove.wizard'].disapprove_sales_orders()



    #inherit from kin_sales_double_validation
    @api.multi
    def action_send_for_confirm(self):
        for order in self:
            order.state = 'waiting'
            order.is_show_btn_send_for_confirm = False
            order.is_show_btn_approve = False
            order.is_show_btn_confirm = True
	    #added this .....on inheritance
	    order.vertical_manager_approve = True
	    order.sales_order_conversion_time_start = datetime.now()

            #Send Email
            company_email = order.env.user.company_id.email.strip()
            #sales_person_email = order.user_id.partner_id.email.strip()

            if company_email:
                # Custom Email Template
                mail_template = order.env.ref('kin_sales_double_validation.mail_templ_send_for_confirmation')
                ctx = {}
                ctx.update({'sale_id':order.id})
                the_url = order._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

                user_ids = []
                group_obj = self.env.ref('kin_sales_double_validation.group_receive_send_for_confirm_email')
                for user in group_obj.users :
                    if user.partner_id.email and user.partner_id.email.strip() :
                        user_ids.append(user.id)
                        ctx = {'system_email': company_email,
                                'confirm_person_email':user.partner_id.email,
                                'confirm_person_name': user.partner_id.name ,
                                'url':the_url
                                }
                        mail_template.with_context(ctx).send_mail(order.id,force_send=False)

                if user_ids :
                    order.message_subscribe_users(user_ids=user_ids)


    @api.multi
    def write(self, vals):
        res = super(SalesExtend, self).write(vals)
        #if len(self.order_line) == 0 :
            #raise UserError(_('At Least an Order Line is Required'))
        self.onchange_reach_limit_extend()
        #self.order_line.name = None
        return res




    def onchange_reach_limit_extend(self):
        for order in self:
            amount_total = order.amount_total
            sale_confirm_limit = self.env.user.sale_confirm_limit
            is_use_sale_confirm_limit = self.env.user.is_use_sale_confirm_limit
	    
            if (amount_total < sale_confirm_limit) and is_use_sale_confirm_limit  and  order.state in ['draft','sent','to_accept']:
                self.env.cr.execute("update sale_order set state = 'so_to_approve' where id = %s" % (self.id))
            elif ((amount_total >= sale_confirm_limit) and is_use_sale_confirm_limit and order.state in ['draft','sent']) :
                self.env.cr.execute("update sale_order set state = 'to_accept' where id = %s" % (self.id))

        	#if company_email and sender_person_email:
	            # Custom Email Template
        	 #   mail_template = self.env.ref('kay_custom.mail_template_send_to_verticals')

	          #  ctx = {'system_email': company_email,
        	   #                'sender_person_name': sender_person_name,
                    #    	   'sender_person_email': sender_person_email,
                #	           'notify_person_email': user.partner_id.email,
	         #                  'notify_person_name': order.user_id.name,
	          #                 'url': sales_order_url,
        	   #                }
                #	    mail_template.with_context(ctx).send_mail(self.id, force_send=False)

	                    #Simulates Notification Dialog Box
        	 #           res = {
                #	        'name': 'Send to Manager Notification',
                 #       	'view_mode': 'form',
	          #              'res_model': 'send.manager.wizard',
        	   #             'type': 'ir.actions.act_window',
                #	        'target': 'new'
        	 #           }



class salelineExtend(models.Model):
    _inherit="sale.order.line"


    freight_and_log = fields.Char(string="Freight and Logistics")
    purchase_price= fields.Float('Cost', digits_compute= dp.get_precision('Product Price'),readonly=False)
    display_in_report = fields.Boolean('Display in Print')
