# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class DirectBranchDeposit(models.Model):
    _name = 'direct.branch.deposit'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    @api.model
    def _default_currency(self):
        company = self.env.user.company_id
        return company.currency_id.id
    
    name = fields.Char('Name', required=True)
    customer_id = fields.Many2one('res.partner', 'Customer', required=True)
    sales_agent_id = fields.Many2one('sales.agent', string='Marketer', required=True)
    branch_id = fields.Many2one('branch.branch', 'Branch', required=True)
    company_id = fields.Many2one('res.company', 'Company',
                default=lambda self: self.env['res.company']._company_default_get('direct.branch.deposit'))
    currency_id = fields.Many2one('res.currency', 'Currency',default=_default_currency)
    state = fields.Selection([('draft', 'Draft'),
                              ('validate', 'Validate')], string="State",
                              default="draft",
                              track_visibility="onchange", readonly=True)
    payment_date = fields.Date('Payment Date',required=True, default=fields.Date.today())
    payment_amount = fields.Float('Payment Amount',required=True)
#     agent_commision = fields.Float('Marketer Commision(%)')
    property_ref_ids = fields.Many2many('sale.property.reference',
                                        'property_reference_deposit_rel'
                                        'deposit_id', 'property_ref_id',
                                        string="Property References")
    payment_id = fields.Many2one('account.payment', 'Payment Ref', readonly=True,copy=False)
#     sales_commission_id = fields.Many2one('sales.commission', string='Sales Commission', required=True)
    journal_id = fields.Many2one('account.journal', 
                                 string='Payment Journal',
                                 domain=[('type', 'in', ('bank', 'cash'))],
                                 required=True)

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        agents = []
        for rec in self:
            if rec.branch_id:
                agent_partner_ids = self.env['sales.agent.partner'].search([('branch_id', '=',  rec.branch_id.id)])
                for partner in agent_partner_ids:
                    agents.append(partner.agent_id.id)
        return {'domain': {'sales_agent_id' : [('id', 'in', agents)]}}
    
    @api.multi
    def action_validate(self):
        for deposit in self:
            saleperson = self.env['sales.agent.partner'].search([('agent_id', '=', deposit.sales_agent_id.id)])
            payment_methods = deposit.journal_id.inbound_payment_method_ids
            payment_method_id = payment_methods and payment_methods[0] or False
            payment = self.env['account.payment'].create({
                'invoice_ids': False,
                'amount': deposit.payment_amount,
                'payment_date': deposit.payment_date or fields.Date.context_today(self),
                'communication': deposit.name,
                'partner_id': deposit.customer_id.id,
                'partner_type': 'customer',
                'journal_id': deposit.journal_id.id,
                'payment_type': 'inbound',
                'payment_method_id': payment_method_id.id,
                'branch_id': deposit.branch_id.id,
                'sale_person_id':saleperson.user_id and saleperson.user_id.id or self.env.user.id,
                'property_ref_ids': [(6, 0, deposit.property_ref_ids.ids)],
            })
            deposit.write({'state': 'validate', 'payment_id': payment.id})