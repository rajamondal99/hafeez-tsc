# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.exceptions import UserError, Warning
from openerp.osv import fields as fields2
import openerp.addons.decimal_precision as dp
from urllib import urlencode
from urlparse import urljoin



class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, context=None):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and has the same
        procurement group, locations and picking type  (moves should already have them identical)
         Otherwise, create a new picking to assign them to.
        """
        move = self.browse(cr, uid, move_ids, context=context)[0]
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1, context=context)
        if picks:
            pick = picks[0]
        else:
            values = self._prepare_picking_assign(cr, uid, move, context=context)
            pick = pick_obj.create(cr, uid, values, context=context)
            # Send the notification
            pick_name = pick_obj.browse(cr,uid,pick,context=context).name
            pick_obj.message_post( cr, uid,pick, body=_('Transfer Document Created -  %s.') % (pick_name),subject='Please see the Newly Created Transfer Picking Document', subtype='mail.mt_comment', context=context)
        res = self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
        return res






class StockPicking(models.Model):
    _inherit = "stock.picking"


    @api.multi
    def action_assign(self):

        super(StockPicking,self).action_assign()
        res2 = {}
        res2['warning'] = {
                              'title' : "Warning: bad value",
                              'message' : "Still Waiting to Restock. Please Purchase the Itemff",
                              }
        #return res
        res = {
                'type': 'ir.actions.client',
                'tag': 'action_client_kin_stock_tag',
                # 'name': 'Warning',
                # 'params': {
                #    'title': 'Warning!',
                #    'text': 'Entered Quantity is greater than quantity on source.',
                #    'sticky': True
                # }
            }

        return  {'type': 'ir.actions.acxddfsrsafsafsfsmts_lose_wizard_and_reload_view'}  # see reference: https://www.odoo.com/forum/help-1/question/how-to-refresh-the-original-view-after-wizard-actions-10268  from Petar





    @api.multi
    def do_unreserve(self):
        super(StockPicking,self).do_unreserve()
        return  {'type': 'ir.actions.act_close_wizard_and_reload_view'}  # see reference: https://www.odoo.com/forum/help-1/question/how-to-refresh-the-original-view-after-wizard-actions-10268  from Petar

    @api.multi
    def close_alert_box(self):
        self.show_alert_box = False
        return

    @api.multi
    def action_cancel(self):
        super(StockPicking,self).action_cancel()
        return  {'type': 'ir.actions.act_close_wizard_and_reload_view'}  # see reference: https://www.odoo.com/forum/help-1/question/how-to-refresh-the-original-view-after-wizard-actions-10268  from Petar


    @api.onchange('location_id')
    def change_location_id(self):
        res = {}
        sale_id = self.sale_id
        status = self.state
        if sale_id and status in ['assigned','partially_available']:

            res['warning'] = {'title' : "Error", 'message' : 'Please click the "Discard" Button, then click "Unreserve" Button, Make the location changes and click "Reserve" button to change the delivery source location', }

            default_rec = self.env['stock.location'].search([('is_default_option','=',True)])
            if not default_rec :
                self.location_id = None
                res['warning'] = {'title' : "Error", 'message' : 'Please set at least one Stock Location in the configuration as "Is default Option" for the system to proceed or click the "Discard" button', }

            else :
                self.location_id = default_rec
            return res

        pack_operation_product_ids = self.pack_operation_product_ids

        for pack_operation_prod in pack_operation_product_ids :
            pack_operation_prod.location_id = self.location_id
            pack_operation_prod.from_loc = self.location_id.name


    @api.onchange('location_dest_id')
    def change_location_dest_id(self):

        pack_operation_product_ids = self.pack_operation_product_ids

        for pack_operation_prod in pack_operation_product_ids :
            pack_operation_prod.location_dest_id = self.location_dest_id
            pack_operation_prod.to_loc = self.location_dest_id.name



    def _get_url(self, module_name,menu_id,action_id, context=None):
        fragment = {}
        res = {}
        model_data = self.env['ir.model.data']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        fragment['menu_id'] = model_data.get_object_reference(module_name,menu_id)[1]
        fragment['model'] =  'account.invoice'
        fragment['view_type'] = 'form'
        fragment['action']= model_data.get_object_reference(module_name,action_id)[1]
        query = {'db': self.env.cr.dbname}

# for displaying tree view. Remove if you want to display form view
#         fragment['page'] = '0'
#         fragment['limit'] = '80'
#         res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


 # For displaying a single record. Remove if you want to display tree view

        fragment['id'] =  context.get("invoice_id")
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))


        return res


# Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line:
            # Load a PO line only once
            if line in self.invoice_line_ids.mapped('purchase_line_id'):
                continue
            if line.product_id.purchase_method == 'purchase':
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
                qty = 0.0
            taxes = line.taxes_id or line.product_id.supplier_taxes_id
            invoice_line_tax_ids = self.purchase_id.fiscal_position_id.map_tax(taxes)
            data = {
                'purchase_line_id': line.id,
                'name': line.name,
                'origin': self.purchase_id.origin,
                'uom_id': line.product_uom.id,
                'product_id': line.product_id.id,
                'account_id': self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
                'price_unit': line.order_id.currency_id.with_context(date=line.order_id.date_order or fields.Date.context_today(self)).compute(line.price_unit, self.currency_id),
                'quantity': qty,
                'discount': 0.0,
                'account_analytic_id': line.account_analytic_id.id,
                'invoice_line_tax_ids': invoice_line_tax_ids.ids,

            }
            account = new_lines.get_invoice_line_account('in_invoice', line.product_id, self.purchase_id.fiscal_position_id, self.env.user.company_id)
            if account:
                data['account_id'] = account.id
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.compute_taxes()
        self.purchase_id = False
        return {}


    def create_vendor_bill(self):

        if not self.purchase_id :
            raise UserError(_('Sorry, Please tell the purchase manager to create purchase orders for items to be received '))


        invoice_obj = self.env['account.invoice']
        invoice_lines = self.env['account.invoice.line']
        for picking_line in self.pack_operation_ids:
            partner = self.partner_id
            if partner :
                journal_domain = [
                        ('type', '=', 'purchase'),
                        ('company_id', '=', partner.company_id.id)
                    ]
                default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
                vals = {
                    'partner_id' : partner.id ,
                    'company_id' : self.company_id.id ,
                    'type' : 'in_invoice' ,
                    'account_id' : partner.property_account_payable_id.id ,
                    'payment_term_id' : partner.property_supplier_payment_term_id.id,
                    'fiscal_position_id' : partner.property_account_position_id.id ,
                    'payment_term_id' : partner.property_supplier_payment_term_id.id ,
                    'partner_bank_id' : partner.bank_ids and partner.bank_ids.ids[0] or False ,
                    'journal_id':default_journal_id.id ,
                }

                purchase_inv = invoice_obj.create(vals)



                    # taxes = picking_line.product_id.supplier_taxes_id
                    # invoice_line_tax_ids = self.purchase_id.fiscal_position_id.map_tax(taxes)
                    # comp_currency = self.env.user.company_id.currency_id

                taxes = picking_line.picking_line.taxes_ids
                invoice_line_tax_ids = self.purchase_id.fiscal_position_id.map_tax(taxes)
                comp_currency = picking_line.currency_id


                data = {
                        'purchase_line_id': picking_line.purchase_line_id,
                        'name': picking_line.purchase_line_id.name,
                        'origin': self.name,
                        'uom_id': picking_line.purchase_line_id.product_uom,
                        'product_id': picking_line.product_id,
                        'account_id': invoice_lines.with_context({'journal_id': default_journal_id.id, 'type': 'in_invoice'})._default_account(),
                        'price_unit': comp_currency.with_context(date=picking_line.date or fields.Date.context_today(self)).compute(picking_line.purchase_line_id.price_unit, comp_currency),
                        'quantity': picking_line.product_qty,
                        'discount': 0.0,
                        'account_analytic_id': picking_line.purchase_line_id.account_analytic_id,
                        'invoice_line_tax_ids': invoice_line_tax_ids.ids,

                }

                account = invoice_lines.get_invoice_line_account('in_invoice', picking_line.product_id, self.purchase_id.fiscal_position_id, self.env.user.company_id)
                if account:
                    data['account_id'] = account.id
                    new_line = invoice_lines.new(data)
                    new_line._set_additional_fields(purchase_inv)
                    invoice_lines += new_line

                    purchase_inv.invoice_line_ids += invoice_lines
                    purchase_inv.compute_taxes()
                    purchase_inv.purchase_id = False
                    return purchase_inv




    @api.multi
    def do_transfer(self):

        #pack_operation_product_ids = self.pack_operation_product_ids
        # for pack_operation_prod in pack_operation_product_ids :
        #     if pack_operation_prod.location_id != self.location_id :
        #         raise UserError(_('Sorry, Source Location should match the source location for the  Operations list '))
        #     if pack_operation_prod.location_dest_id != self.location_dest_id :
        #         raise UserError(_('Sorry, Destination Location should match the Destination location for the  Operations list '))


        res = super(StockPicking,self).do_transfer()


        is_create_invoice = self.picking_type_id.is_create_invoice
        if is_create_invoice :
            # Create the invoice
            invoice_obj = self.env['account.invoice']
            sale_order = self.sale_id
            picking_type_code = self.picking_type_code
            invoic_obj = self.invoice_id or False
            if picking_type_code == "incoming" and sale_order and invoic_obj : # Create a Customer refund invoice

                invoice_refund = self.env['account.invoice.refund']
                invoice_refund_obj= invoice_refund.create({'description':' Inventory Return from Customer for %s'% self.name,'filter_refund':'refund'})
                ctx = {'active_ids': [invoic_obj.id]}
                invoice_refund_obj.env.context = ctx
                return_obj = invoice_refund_obj.compute_refund()
                invo_id = return_obj['domain'][1][2][0]
                invref_obj = invoice_obj.browse(invo_id)
                self.invoice_refund_id = invref_obj
                invref_obj.message_post( _('Customer Refund Invoice Created for Returned Inventory %s.') % (self.name),subject='Please See the Created Refund Invoice from Customer Inventory Return', subtype='mail.mt_comment')


            if picking_type_code == "outgoing" and sale_order   : # Create a Customer Invoice
                inv_id = sale_order.action_invoice_create()
                inv_obj = invoice_obj.browse(inv_id)[0]
                inv_obj.sale_id = sale_order
                inv_obj.picking_id = self
                self.invoice_id = inv_obj
                self.sale_id = sale_order
                inv_obj.message_post( _('Invoice Created for Delivered Inventory %s.') % (self.name),subject='Please See the Created Invoice for Delivered Inventory', subtype='mail.mt_comment')

                #Send Invoice Notification to Selected Users
                is_send_invoice_notification = self.picking_type_id.is_send_invoice_notification
                company_email = self.env.user.company_id.email.strip()
                if is_send_invoice_notification and company_email :
                    # Custom Email Template
                    mail_template = self.env.ref('kin_stock.mail_templ_invoice_delivery')
                    the_url = inv_obj._get_url('account','menu_action_invoice_tree1','action_invoice_tree1')
                    users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                    for user in users :
                        if user.has_group('kin_stock.group_receive_inventory_invoice_email') and user.partner_id.email.strip() :
                            ctx = {'system_email': company_email,
                                   'accountant_email':user.partner_id.email,
                                   'accountant_name': user.partner_id.name ,
                                   'url':the_url,
                                    'origin': inv_obj.origin
                                   }
                            mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                            self.show_alert_box = True




############################################################################################
        ######   FOR PURCHASES VENDOR BILLS AND PURCHASE RETURNS


            purchase_order = self.purchase_id
            if picking_type_code == "incoming" and purchase_order : # Create a Vendor Bill
                vendor_bill =  False
                if vendor_bill :
                    vendor_bill.purchase_id1 = purchase_order    # store the purchase id
                    vendor_bill.picking_id = self
                    self.invoice_id = vendor_bill
                    self.purchase_id = purchase_order

                    # No need for this since we it should affect all mail.message. the create() was overridden for the mail.message model
                    #ctx_copy= self.env.context.copy()
                    #ctx_copy.update({'mail_notify_force_send':False})
                    #purchase_inv.with_context(ctx_copy).message_post( _('Invoice Created for Inventory Received  %s.') % (self.name),subject='Created Invoice from Goods Received into the Inventory', subtype='mail.mt_comment')


                    vendor_bill.message_post( _('Invoice Created for Received Inventory %s.') % (self.name),subject='Please See the Created Invoice for Goods Received into the Inventory', subtype='mail.mt_comment')

                    # Send Email to the Accountant
                    company_email = self.env.user.company_id.email.strip()
                    if company_email :
                        # Custom Email Template
                        mail_template = self.env.ref('kin_stock.mail_templ_purchase_bill_created')
                        ctx = {}
                        ctx.update({'invoice_id':vendor_bill.id})
                        the_url = self._get_url('account','menu_action_invoice_tree2','action_invoice_tree2',ctx)
                        users = self.env['res.users'].search([('active','=',True),('company_id', '=', self.env.user.company_id.id)])

                        for user in users :
                            if user.has_group('kin_stock.group_receive_purchase_bill_email') and user.partner_id.email.strip() :
                                ctx = {'system_email': company_email,
                                        'accountant_email':user.partner_id.email,
                                        'accountant_name': user.partner_id.name ,
                                        'url':the_url,
                                       'picking_id' : self.name,
                                       'purchase_id' : purchase_order.name

                                    }
                                mail_template.with_context(ctx).send_mail(self.id,force_send=False)
                                self.show_alert_box = True


            prev_picking_obj = self.previous_picking_id
            if prev_picking_obj :
                prev_purchase_order = prev_picking_obj.purchase_id or False
                prev_invoice_id = prev_picking_obj.invoice_id or False
                if picking_type_code == "outgoing" and prev_purchase_order and prev_invoice_id  : # Create a Return goods Invoice

                    prev_invoice_refund = self.env['account.invoice.refund']
                    prev_invoice_refund_obj= prev_invoice_refund.create({'description':' Inventory Return to Vendor for %s'% self.name,'filter_refund':'refund'})
                    prev_ctx = {'active_ids': [prev_invoice_id.id]}
                    prev_invoice_refund_obj.env.context = prev_ctx
                    prev_return_obj = prev_invoice_refund_obj.compute_refund()
                    prev_invo_id = prev_return_obj['domain'][1][2][0]
                    prev_invref_obj = invoice_obj.browse(prev_invo_id)
                    self.supplier_invoice_refund_id = prev_invref_obj
                    prev_invref_obj.message_post( _('Vendor Refund Invoice Created for Returned Inventory %s.') % (self.name),subject='Please See the Created Refund Invoice to Vendor Inventory Return',subtype='mail.mt_comment')


        return res




    @api.multi
    def btn_view_invoices(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        return {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.invoice_id])],
            #'context': context,
            # 'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox').id,
            #'res_id': self.env.context.get('cashbox_id'),
            'target': 'new'
        }

    @api.multi
    def btn_view_po(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        return {
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.purchase_id])],
            #'context': context,
            # 'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox').id,
            #'res_id': self.env.context.get('cashbox_id'),
            'target': 'new'
        }

    @api.multi
    def btn_view_so(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        return {
            'name': _('Sales Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.sale_id])],
            #'context': context,
            # 'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox').id,
            #'res_id': self.env.context.get('cashbox_id'),
            'target': 'new'
        }

    @api.one
    @api.depends('invoice_id')
    def _compute_invoice_count(self):
            self.invoice_count = len(self.invoice_id)



    @api.depends('purchase_id')
    def _compute_po_count(self):
        for rec in self :
            rec.po_count = len(rec.purchase_id)


    @api.depends('sale_id')
    def _compute_so_count(self):
        for rec in self :
            rec.so_count = len(rec.sale_id)


    # def _compute_invoice(self):
    #     for picking in self:
    #         invoices = picking.sale_id.invoice_ids
    #         for line in picking.sale_id.invoice_ids:
    #             invoices |= line.invoice_lines.mapped('invoice_id')
    #         picking.invoice_ids = invoices
    #         picking.invoice_count = len(invoices)



    invoice_id = fields.Many2one('account.invoice')
    invoice_refund_id = fields.Many2one('account.invoice')
    supplier_invoice_refund_id = fields.Many2one('account.invoice')
    previous_picking_id = fields.Many2one('stock.picking')
    invoice_count = fields.Integer(compute="_compute_invoice_count", string='# of Invoices', copy=False, default=0)
    po_count = fields.Integer(compute="_compute_po_count", string='# of Purchase Orders', copy=False, default=0)
    so_count = fields.Integer(compute="_compute_so_count", string='# of Sales Orders', copy=False, default=0)
    #invoice_ids = fields.Many2many('account.invoice', compute="_compute_invoice", string='Invoices', copy=False)
    operation_type = fields.Selection(related='picking_type_id.code', store=True)
    shipment_ref = fields.Char(string='Shipment Reference')
    show_alert_box  = fields.Boolean(string="Show Alert Box")

class Message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        ctx_copy= self.env.context.copy()
        ctx_copy.update({'mail_notify_force_send':False})
        res = super(Message,self.with_context(ctx_copy)).create(values)
        return res



class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        # Prevent copy of the carrier and carrier price when generating return picking
        # (we have no integration of returns for now)
        new_picking, pick_type_id = super(StockReturnPicking, self)._create_returns()

        prev_picking = self.env.context.get('active_id',False)
        if prev_picking and new_picking :
            picking_obj = self.env['stock.picking'].browse(prev_picking)
            new_picking_obj = self.env['stock.picking'].browse(new_picking)
            # save the previous picking id
            new_picking_obj.previous_picking_id = picking_obj
        return new_picking, pick_type_id




class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_default_option = fields.Boolean(string="Is Default Option", help="This must be set for at least one Stock Location. ")
    is_dont_show_location = fields.Boolean(string="Don't Show in List", help="Don't Show this location in the Stock Picking Form Location List. ")


    @api.model
    def create(self,vals):
        is_default_option = vals.get('is_default_option',False)
        if is_default_option :
            vals['usage'] = 'view'
        res = super(StockLocation,self).create(vals)
        return res


    @api.multi
    def write(self,vals):
        is_default_option = vals.get('is_default_option',None)
        if is_default_option == None :
            is_default_option = self.is_default_option
        if is_default_option :
            vals['usage'] = 'view'
        res = super(StockLocation,self).write(vals)
        return  res

class StockPickingTye(models.Model):
    _inherit = "stock.picking.type"

    is_create_invoice = fields.Boolean(string="Create Invoice after Operation")
    is_send_invoice_notification = fields.Boolean(string="Send Invoice Notification",help="This allows the system to automatically send invoice notification to the selected users in the user access right configuration")


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.onchange('qty_done')
    def change_qty_done(self):
        res = {}
        for rec in self :
            if rec.qty_done > rec.product_qty :
                res['warning'] = {'title' : "Error", 'message' : _('Delivery Qty is higher that the Quantity to be Delivered') }
                self.qty_done = 0
                return  res


    @api.model
    def create(self,vals):
        return super(StockPackOperation,self).create(vals)


    # @api.depends('product_qty', 'price_unit', 'tax_ids')
    # def _compute_amount(self):
    #     for picking_line in self:
    #         taxes = picking_line.taxes_ids.compute_all(picking_line.price_unit, picking_line.currency_id, picking_line.product_qty, product=picking_line.product_id, partner=picking_line.partner_id)
    #
    #         self.price_total = taxes['total_included']
    #         self.price_tax = taxes['total_included'] - taxes['total_excluded']
    #         self.price_subtotal = taxes['total_excluded']


    purchase_line_id = fields.Many2one('purchase.order.line')
    price_subtotal = fields.Float(string='Subtotal')
    price_total = fields.Float( string='Total')
    price_tax = fields.Float( string='Tax')



class StockQuant(models.Model):
    _inherit = "stock.quant"

    cost_price = fields.Float(string="Initial Unit Cost", type='float', readonly=True)


    @api.model
    def create(self,vals):
        vals['cost_price'] = vals['cost']
        return super(StockQuant,self).create(vals)


class StockMove(models.Model):
    _inherit = "stock.move"

    state = fields.Selection([('draft', 'New'),
                                   ('cancel', 'Cancelled'),
                                   ('waiting', 'Waiting Another Move'),
                                   ('confirmed', 'Waiting Availability'),
                                   ('assigned', 'Available and Reserved'),
                                   ('done', 'Done'),
                                   ], 'Status', readonly=True, select=True, copy=False,
                 help= "* New: When the stock move is created and not yet confirmed.\n"\
                       "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n"\
                       "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to me manufactured...\n"\
                       "* Available: When products are reserved, it is set to \'Available\'.\n"\
                       "* Done: When the shipment is processed, the state is \'Done\'.")





