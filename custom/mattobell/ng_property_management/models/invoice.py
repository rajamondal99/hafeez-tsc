# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    need_property_ref = fields.Boolean(string='Need Property Ref', help='Tick this box if sales order needs property reference on sales order line.', copy=True, default=True, readonly=True)
    branch_id = fields.Many2one('branch.branch', string='Branch', copy=True, readonly=True)

    @api.multi
    def action_move_create(self):
        # for inv in self:
        #     agent_partner_ids = self.env['sales.agent.partner'].search([('agent_id', '=', inv.agent_id.id)])
        #     user_ids = [partner.user_id.id for partner in agent_partner_ids]
        #     user = user_ids and user_ids[0] or False
        #     if inv.user_id.id != user and inv.type == 'out_invoice' and inv.apply_sales_commission:
        #         raise Warning(_('Salesperson must be same as selected Marketer.'))
        return super(AccountInvoice, self).action_move_create()
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        user = self.env.user
        if self.user_has_groups('ng_property_management.group_branch'):
            partner = self.env.user.partner_id
            if partner.branch_id:
                args += [('branch_id', '=', partner.branch_id.id)]
        return super(AccountInvoice, self).search(args, offset, limit, order, count=count)

    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    preoperty_ref_id = fields.Many2one('sale.property.reference', string='Property Reference', readonly=False, copy=False)
    property_installment_id = fields.Many2one('product.installment.config', string='Property Installment')

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    branch_id = fields.Many2one('branch.branch', string='Branch', copy=True, readonly=True)
 
    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec.update(branch_id = invoice['branch_id'] and invoice['branch_id'][0] or False)
        return rec
