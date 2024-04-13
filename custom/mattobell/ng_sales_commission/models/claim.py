# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ClaimOrder(models.Model):
    _name = 'claim.order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def _default_currency(self):
        company = self.env.user.company_id
        return company.currency_id.id
        
        
    name = fields.Char('Name', default='/')
    journal_id = fields.Many2one('account.journal', 
                                 string='Payment Method',
                                 domain=[('type', 'in', ('bank', 'cash'))],
                                 required=True)
    payment_date = fields.Date('Payment Date',required=True, default=fields.Date.today())
    payment_amount = fields.Float('Payment Amount',required=True)
    customer_id = fields.Many2one('res.partner', 'Customer')
    state = fields.Selection([('draft', 'Draft'),
                              ('validate', 'Validate'),
                              ('approve', 'Approve'),
                              ('posted', 'Posted'),
                              ('cancel', 'Cancelled')], string="State",
                             default="draft",
                              track_visibility="onchange", readonly=True)
    company_id = fields.Many2one('res.company', 'Company',
                default=lambda self: self.env['res.company']._company_default_get('claim.order'))
    currency_id = fields.Many2one('res.currency', 'Currency',default=_default_currency)
    sales_agent_id = fields.Many2one('sales.agent', string='Marketer', required=False)
    agent_commision = fields.Float('Marketer Commision(%)')
    branch_id = fields.Many2one('branch.branch', 'Branch', required=False)
    invoice_line_ids = fields.Many2many('account.invoice.line',
                                        'claim_id', 'line_id',
                                        string="Invoice Lines")
    property_ref_ids = fields.Many2many('sale.property.reference',
                                        'property_reference_claim_rel'
                                        'claim_id', 'property_ref_id',
                                        string="Property References")
    payment_id = fields.Many2one('account.payment', 'Payment Ref', readonly=True)
    sales_commission_id = fields.Many2one('sales.commission', string='Sales Commission', required=False)
    
    @api.onchange('branch_id')
    def onchange_branch_id(self):
        agents = []
        for rec in self:
            if rec.branch_id:
                agent_partner_ids = self.env['sales.agent.partner'].search([('branch_id', '=',  rec.branch_id.id)])
                for partner in agent_partner_ids:
                    agents.append(partner.agent_id.id)
        return {'domain': {'sales_agent_id' : [('id', 'in', agents)]}}
                
    
    @api.onchange('sales_commission_id')
    def onchange_sales_commission(self):
        for claim in self:
            claim.agent_commision = claim.sales_commission_id.agent_commision
        
        
    @api.onchange('customer_id')
    def onchange_customer(self):
        for claim in self:
            claim.invoice_line_ids = False
            invoice_ids = self.env['account.invoice'].search([('state', '=', 'paid'),
                                                              ('type', '=', 'out_invoice'),
                                                              ('partner_id', '=',  claim.customer_id.id)])
            invoice_lines = []
            if invoice_ids:
                for invoice in invoice_ids:
                    invoice_line_ids = self.env['account.invoice.line'].search(
                        [('id', 'in', invoice.invoice_line_ids.ids),
                        ('preoperty_ref_id', '!=', False)]).ids
                    invoice_lines.extend(invoice_line_ids)
            else:
                invoice_line_ids = self.env['account.invoice.line'].search(
                    [('invoice_id.state', '=', 'paid'),
                    ('invoice_id.type', '=', 'out_invoice'),
                    ('preoperty_ref_id', '!=', False)]).ids
                invoice_lines.extend(invoice_line_ids)
            # create domain for property reference lines
            sale_ids = self.env['sale.order'].search([('partner_id', '=', claim.customer_id.id),
                                                      ('property_ref_generated', '=', True),
                                                      ('state', 'not in', ('done', 'cancel', 'draft'))])
            sale_line_list = []
            for sale in sale_ids:
                if sale.invoice_ids:
                    if sale.invoice_ids[0].state == 'open':
                        sale_line_list.extend(sale.order_line.ids)
            property_ref_ids = self.env['sale.property.reference'].search([('sale_line_id', 'in', sale_line_list)])
            return {'domain': {'invoice_line_ids': [('id', 'in', invoice_lines)],
                               'property_ref_ids': [('id', 'in', property_ref_ids.ids)]}}
            
            
    @api.multi
    def action_validate(self):
        for claim in self:
            if claim.name == '/':
                name = self.env['ir.sequence'].next_by_code('claim.order') or '/'
            claim.write({'state': 'validate', 'name': name})
            
    @api.multi
    def action_approve(self):
        for claim in self:
            claim.write({'state': 'approve'})

    @api.multi
    def action_post(self):
        for claim in self:
            
            saleperson = self.env['sales.agent.partner'].search([('agent_id', '=', claim.sales_agent_id.id)])
            payment_methods = claim.journal_id.inbound_payment_method_ids
            payment_method_id = payment_methods and payment_methods[0] or False
            payment = self.env['account.payment'].create({
                'invoice_ids': False,
                'amount': claim.payment_amount,
                'payment_date': claim.payment_date or fields.Date.context_today(self),
                'communication': claim.name,
                'partner_id': claim.customer_id.id,
                'partner_type': 'customer',
                'journal_id': claim.journal_id.id,
                'payment_type': 'inbound',
                'payment_method_id': payment_method_id.id,
                'branch_id': claim.branch_id.id,
                'apply_sales_commission':True,
                'sales_commision_id': claim.sales_commission_id and claim.sales_commission_id or False,
                'agent_commision':claim.agent_commision,
                'sale_person_id':saleperson.user_id and saleperson.user_id.id or self.env.user.id,
                'property_ref_ids': [(6, 0, claim.property_ref_ids.ids)],
            })
            claim.write({'state': 'posted', 'payment_id': payment.id})
            
    @api.multi
    def action_cancel(self):
        for claim in self:
            claim.write({'state': 'cancel'})
            
    @api.multi
    def unlink(self):
        for claim in self:
            if claim.state not in ('draft', 'cancel'):
                raise Warning(_('Cannot delete claim(s) which are already validated or posted.'))
        return super(ClaimOrder, self).unlink()
