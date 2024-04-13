# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class SalePropertyReference(models.Model):
    _name = 'sale.property.reference'
    
    name = fields.Char(string='Property Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line')
    product_id = fields.Many2one('product.product',related='sale_line_id.product_id',
                                 string="Product")
    order_id = fields.Many2one('sale.order',related='sale_line_id.order_id',
                                 string="Order")
    agent_id = fields.Many2one('sales.agent',related='order_id.agent_id', string='Marketer', readonly=True)
    branch_id = fields.Many2one('branch.branch',related='order_id.branch_id',string='Branch', readonly=True)
    zone_id = fields.Many2one('zone.zone',related='branch_id.zone_id',string='Zone', readonly=True)


class Sale(models.Model):
    _inherit = 'sale.order'
    
    agent_id = fields.Many2one('sales.agent', string='Marketer', copy=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    branch_id = fields.Many2one('branch.branch', string='Branch', copy=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    property_ref_generated = fields.Boolean(string='Property Ref Generated', copy=False, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    need_property_ref = fields.Boolean(string='Need Property Ref', help='Tick this box if sales order needs property reference on sales order line.', copy=True, default=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    
    
    @api.onchange('branch_id')
    def onchange_branch_id(self):
        agents = []
        for rec in self:
            if rec.branch_id:
                agent_partner_ids = self.env['sales.agent.partner'].search([('branch_id', '=',  rec.branch_id.id)])
                for partner in agent_partner_ids:
                    agents.append(partner.agent_id.id)
        return {'domain': {'agent_id' : [('id', 'in', agents)]}}
                
                
    
    @api.multi
    def _prepare_invoice(self):
        result = super(Sale, self)._prepare_invoice()
        need_property_ref = self.need_property_ref
        result.update({'need_property_ref' : need_property_ref,
                       'branch_id': self.branch_id and self.branch_id.id or False})
        return result
    
    @api.onchange('agent_id')
    def onchange_agent(self): 
        if self.agent_id:
            agent_partner_ref = self.env['sales.agent.partner'].search([('agent_id', '=', self.agent_id.id)])
            if agent_partner_ref:
                self.user_id = agent_partner_ref.user_id.id

    @api.multi
    def generate_account_no(self):
        for record in self:
            for line in record.order_line:
                if not record.need_property_ref:
                    raise Warning(_('No need of property reference.'))
                if not line.preoperty_ref_id: 
                    number = self.env['ir.sequence'].next_by_code('property.number')
                    property = self.env['sale.property.reference'].\
                        create({'name': number, 
                                'partner_id': record.partner_id.id,
                                'sale_line_id': line.id})
#                 line.account_no = self.env['ir.sequence'].next_by_code('property.number')
                    line.preoperty_ref_id = property.id
            record.property_ref_generated = True
        
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        user = self.env.user
        if self.user_has_groups('ng_property_management.group_branch'):
            partner = self.env.user.partner_id
            if partner.branch_id:
                args += [('branch_id', '=', partner.branch_id.id)]
        return super(Sale, self).search(args, offset, limit, order, count=count)

    @api.multi
    def action_confirm(self):
        for order in self:
            if order.need_property_ref:
                for ord_line in order.order_line:
                    if not ord_line.preoperty_ref_id.id:
                        raise Warning(_('Please generate property reference.'))
        return super(Sale, self).action_confirm()
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if res:
            res.update({"preoperty_ref_id": self.preoperty_ref_id.id,
                         "property_installment_id":self.property_installment_id.id,
                         'agent_commision': self.agent_commision})
        return res
    
#     account_no = fields.Char(string='Property Reference', readonly=True, copy=False)
    preoperty_ref_id = fields.Many2one('sale.property.reference', string='Property Reference', readonly=False, copy=False)
    property_installment_id = fields.Many2one('product.installment.config', string='Property Installment')
    agent_commision = fields.Float('Marketer Commision(%)')
    
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"
    
    @api.model
    def _get_customer(self):
        if self._context and self._context.get('active_id', False):
            return self.env['sale.order'].browse(self._context['active_id']).partner_id

    preoperty_ref_id = fields.Many2one('sale.property.reference', string='Property Reference')
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, default=_get_customer) 
    plot_product_id = fields.Many2one('product.product', string='Product/Plot')
    property_installment_id = fields.Many2one('product.installment.config', string='Property Installment')
    agent_commision = fields.Float('Marketer Commision(%)')
    
    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        res.need_property_ref = order.need_property_ref
        res.branch_id = order.branch_id and order.branch_id.id or False
        for line in res.invoice_line_ids:
            line.preoperty_ref_id = self.preoperty_ref_id.id
            line.property_installment_id = self.property_installment_id.id
        return res

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    partner_id = fields.Many2one(domain="[('customer', '=', True)]")