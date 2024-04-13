from openerp import models, fields,api
from datetime import datetime


class PurchaseExtend(models.Model):
    _inherit = 'purchase.order'

    delivery_order = fields.Many2one('stock.picking',string="Delivery order",domain=[('state','in',['confirmed'])])
    purchase_order_approve_time_start = fields.Datetime(string="purchase order approve time start",default=fields.datetime.now(),readonly=True)
    purchase_order_approve_time_end = fields.Datetime(string="purchase order approve time end",readonly=True)
    purchase_order_aproved = fields.Boolean(default=False)
    finance_vendor_bill_creation_start_time = fields.Datetime(string="Vendor bil time start",readonly=True)
    finance_vendor_bill_creation_end_time = fields.Datetime(string="Vendor bill time end",readonly=True)
    finance_vendor_bill_created = fields.Boolean(default=False,string="Veendor bill Created")
    purchase_request_id = fields.Many2one("purchase.request",string="Purchase Request")
    sale_order_id = fields.Many2one("sale.order",string="Reference SO")


    @api.onchange('purchase_request_id')
    @api.multi
    def _compute_request(self):
        request_obj = self.env['purchase.request']
        requests = request_obj.search([('id', "=", self.purchase_request_id.id)])
        lines = []
        for request in requests.line_ids:
            lines.append((0, 0, {
                    'product_id':request.product_id.id,
                    'product_qty': request.product_qty,
                    'date_planned':fields.datetime.now(),
                       'product_uom':request.product_id.uom_id.id,


            })  
            )
        self.order_line = lines
        self.sale_order_id = requests.sale_order_id.id



    @api.onchange('delivery_order')
    @api.multi
    def _compute_delivery(self):
        for dev in self:
	    delivery_obj = self.env['stock.picking'].search([['id','=',dev.delivery_order.id]])
	    if delivery_obj.state == 'confirmed':
	        delivery_obj.update({'purchase_draft_po_approval_done':True})
	

    @api.model
    def po_approval_timeout(self):
	print(self.env.user.company_id.x_time_start)
        stock_pick_obj = self.env['purchase.order'].search([('create_date','>',self.env.user.company_id.x_time_start)])
        #sales_order_ids = self.pool.get('sale.order').search(cr, uid, [])
       

        for order in stock_pick_obj:
            time_difference = 0

            if not order.purchase_order_approve_time_end and order.purchase_order_approve_time_start and not order.purchase_order_aproved:
                
                 d1=datetime.strptime(str(fields.datetime.now()),'%Y-%m-%d %H:%M:%S.%f') 
                 d2=datetime.strptime(str(order.purchase_order_approve_time_start),'%Y-%m-%d %H:%M:%S')
                 time_difference = d1 - d2
                 print(time_difference.total_seconds()/60)
                 if float(str(time_difference.total_seconds()/60)) >  15.0:
                     order.update({'purchase_order_approve_time_end':datetime.now()})
                     ctx = {}
                   

                     #notify HR Manager
                     if not order.purchase_order_aproved and order.purchase_order_approve_time_start:
                         history_obj = self.env['timeout.history']
                         history_obj.create({'name':'Purchase Order Approval Timeout','user_id':'Purchase Manager','document_id':order.name,'time_start':order.purchase_order_approve_time_start,'time_end':order.purchase_order_approve_time_end,'time_range':'10 minutes'})
                         message_obj = self.env['mail.message']
                         company_email = self.env.user.company_id.email.strip()
                         mail_template = self.env.ref('kay_custom.mail_template_send_to_verticals')

                         group_obj = self.env.ref('base.group_hr_manager')
                         if group_obj:
                             for user in group_obj.users:
                                 if user.partner_id.email and user.partner_id.email.strip():
                                  


                                     ctx = {'system_email': company_email,
                                           'origin':order.name ,
                                           'saleperson':'Purchase Manager',
                                            'hr_email':user.partner_id.id,
                                            'url':'',
                                             }
                                     mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                        

            #handel finance timeout
	    
	    elif not order.finance_vendor_bill_creation_end_time and order.finance_vendor_bill_creation_start_time and not order.finance_vendor_bill_created:
            
                 d1=datetime.strptime(str(fields.datetime.now()),'%Y-%m-%d %H:%M:%S.%f') 
                 d2=datetime.strptime(str(order.finance_vendor_bill_creation_start_time),'%Y-%m-%d %H:%M:%S')
                 time_difference = d1 - d2
               
                 if float(str(time_difference.total_seconds()/60)) >  15.0:
                     order.update({'finance_vendor_bill_creation_end_time':datetime.now()})
                     ctx = {}
                     #ctx.update({'sale_id':order.id})
                     #quote_url = order._get_sale_order_url('sale','menu_sale_order','action_orders',ctx)

                     #notify HR Manager
                     if not order.finance_vendor_bill_created and order.finance_vendor_bill_creation_start_time:
                         history_obj = self.env['timeout.history']
                         history_obj.create({'name':'Vendor bill creation Timeout','user_id':'Accountant','document_id':order.name,'time_start':order.finance_vendor_bill_creation_start_time,'time_end':order.finance_vendor_bill_creation_end_time})
                         message_obj = self.env['mail.message']
                         company_email = self.env.user.company_id.email.strip()
                         mail_template = self.env.ref('kay_custom.mail_template_send_to_verticals')


                         group_obj = self.env.ref('base.group_hr_manager')
		         if group_obj:
                             for user in group_obj.users:
                                 if user.partner_id.email and user.partner_id.email.strip():
                                     #user_ids.append(user.id)


                                     ctx = {'system_email': company_email,
                                            'origin':order.name ,
                                             'saleperson':'Purchase Manager',
                                             'hr_email':user.partner_id.email,
                                             'url':'',
                                       }
                                     mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                        






    def confirm_po(self):
        if self.state == 'to approve' :
	    self.purchase_order_aproved = True
	    self.finance_vendor_bill_creation_start_time = fields.datetime.now()
	   
            #send email
            company_email = self.env.user.company_id.email.strip()
            purchase_person_email = self.user_id.partner_id.email.strip()
            purchase_person_name = self.user_id.partner_id.name

            if company_email and purchase_person_email:
                # Custom Email Template
                mail_template = self.env.ref('kin_purchase.mail_templ_rfq_confirmed')
                ctx = {}
                ctx.update({'purchase_id': self.id})
                the_url = self._get_purchase_url('purchase', 'menu_purchase_form_action', 'purchase_form_action', ctx)

                user_ids = []
                group_obj = self.env.ref('kin_purchase.group_receive_rfq_confirmed_email')
                for user in group_obj.users:
                    if user.partner_id.email and user.partner_id.email.strip():
                        user_ids.append(user.id)
                        ctx = {
                            'system_email': company_email,
                            'purchase_person_name': purchase_person_name,
                            'purchase_person_email': purchase_person_email,
                            'notify_person_email': user.partner_id.email,
                            'notify_person_name': user.partner_id.name,
                            'url': the_url
                        }
                        mail_template.with_context(ctx).send_mail(self.id, force_send=False)
                        self.message_subscribe_users(user_ids=user_ids)

            return {}

    @api.multi
    def button_confirm(self):
        if self.po_name :
            self.name = self.po_name
        else :
            self.rfq_name = self.name
            self.name = self.env['ir.sequence'].get('po_id_code')
            self.po_name = self.name
        res = super(PurchaseExtend,self).button_confirm()
        self.confirm_po()
        self.purchase_order_aproved = True
        self.finance_vendor_bill_creation_start_time = fields.datetime.now()

        is_create_invoice_after_po_confirm  = self.env.user.company_id.is_create_invoice_after_po_confirm

        if is_create_invoice_after_po_confirm :
            invoice_obj = self.env['account.invoice']
            for order in self:
                partn = order.partner_id
                if partn :
                        journal_domain = [
                            ('type', '=', 'purchase'),
                            ('company_id', '=', partn.company_id.id)
                        ]
                        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
                        analytic_account_id = default_journal_id.analytic_account_id or False
                        vals = {
                            'partner_id' : partn.id ,
                            'company_id' : order.company_id.id ,
                            'type' : 'in_invoice' ,
                            'account_id' : partn.property_account_payable_id.id ,
                            'payment_term_id' : partn.property_supplier_payment_term_id.id,
                            'fiscal_position_id' : partn.property_account_position_id.id ,
                            'payment_term_id' : partn.property_supplier_payment_term_id.id ,
                            'partner_bank_id' : partn.bank_ids and partn.bank_ids.ids[0] or False ,
                            'journal_id':default_journal_id.id ,
                            'origin':order.name,

                        }

                        purchase_inv = invoice_obj.create(vals)
                        purchase_inv.purchase_id = order
                        ans = purchase_inv.purchase_order_change()

                        purchase_inv.message_post( _('Invoice Created for Purchase Order  %s.') % (order.name),subject='Please See the Created Invoice for the Purchased Order', subtype='mail.mt_comment')

                        # Send Email to the Accountant
                        company_email = self.env.user.company_id.email.strip()
                        if company_email :
                            # Custom Email Template
                            mail_template = self.env.ref('kin_purchase.mail_templ_purchase_bill_created_on_ordered_qty')
                            ctx = {}
                            ctx.update({'invoice_id':purchase_inv.id})
                            the_url = self._get_url_account_invoice('account','menu_action_invoice_tree2','action_invoice_tree2',ctx)
                            users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                            for user in users :
                                if user.has_group('kin_stock.group_receive_purchase_bill_email') and user.partner_id.email and user.partner_id.email.strip() :
                                    ctx = {'system_email': company_email,
                                            'accountant_email':user.partner_id.email,
                                            'accountant_name': user.partner_id.name ,
                                            'url':the_url,
                                           'purchase_id' : self.name,
                                            'partner_name' : self.partner_id.name

                                        }
                                    mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                                    self.show_alert_box = True
        return res




class PurchaseRequestExtend(models.Model):
    _inherit =  "purchase.request"


    @api.onchange('sale_order_id')
    def _compute_order_lines(self):
            request_obj = self.env['sale.order']
            requests = request_obj.search([('id', "=", self.sale_order_id.id)])
            lines = []
            for request in requests.order_line:
                lines.append((0, 0, {
                    'product_id':request.product_id.id,
                    'product_qty': request.product_uom_qty,
	            'date_required':fields.datetime.today(),
                       'product_uom_id':request.product_id.uom_id.id,
		

                })  
                )
            self.line_ids = lines


