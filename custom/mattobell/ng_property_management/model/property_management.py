# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ProductInstallmentConfig(models.Model):
    _name = 'product.installment.config'
    _description = 'product.installment.config'
    
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Installment Name', required=True)
    total_sale_price = fields.Float(string='Sales Price', required=True)
    total_number_installment = fields.Integer(string='Number of Installment', required=True)
    agent_commision = fields.Float(string='Sales Agent Commission(%)', required=False)


class SalesAgent(models.Model):
    _name = 'sales.agent'
    _description = 'Sales.Agent'
    
    name = fields.Char(string='Name', required=True)

class SalesAgentPartner(models.Model):
    _name = 'sales.agent.partner'
    _description = 'Sales.Agent.Partner'
     
    agent_id = fields.Many2one('sales.agent', required=True, string='Agent')
    partner_id = fields.Many2one('res.partner', required=True, string='Related Partner')
    user_id = fields.Many2one('res.users', required=True, string='Related User')
    #commission_ids = fields.One2many('sales.agent.commision', 'commission_id')
    
    _sql_constraints = [
           ('agent_id_uniq',
            'unique(agent_id)',
            'Sales Agent must be unique.'),
       ]

class SalesAgentCommision(models.Model):
    _name = 'sales.agent.commision'
    _description = 'Sales.Agent.Commision'
    
    commission_id = fields.Many2one('sales.agent.partner', required=False, string='Commission')
    no_months = fields.Integer(string='Number of Months', required=True)
    commission_percentage = fields.Float(string='Commission Percentage', required=True)

class Product(models.Model):
    _inherit = 'product.product'
    
    intallment_ids = fields.One2many('product.installment.config', 'product_id', copy=True)
    
class Sale(models.Model):
    _inherit = 'sale.order'
    
    agent_id = fields.Many2one('sales.agent', string='Sales Agent', copy=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    property_ref_generated = fields.Boolean(string='Property Ref Generated', copy=False, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    need_property_ref = fields.Boolean(string='Need Property Ref', help='Tick this box if sales order needs property reference on sales order line.', copy=True, default=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    
    @api.multi
    def _prepare_invoice(self):
        result = super(Sale, self)._prepare_invoice()
        need_property_ref = self.need_property_ref
        result.update({'need_property_ref' : need_property_ref})
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
                    property = self.env['sale.property.reference'].create({'name': number,'partner_id': record.partner_id.id})
#                 line.account_no = self.env['ir.sequence'].next_by_code('property.number')
                    line.preoperty_ref_id = property.id
            record.property_ref_generated = True
        
    @api.multi
    def action_confirm(self):
        if self.need_property_ref:
            for ord_line in self.order_line:
                if not ord_line.preoperty_ref_id.id:
                    raise Warning(_('Please generate property reference.'))
        return super(Sale, self).action_confirm()
    
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"
    
    @api.model
    def _get_customer(self):
        return self.env['sale.order'].browse(self._context['active_id']).partner_id

    preoperty_ref_id = fields.Many2one('sale.property.reference', string='Property Reference')
    partner_id = fields.Many2one('res.partner', string='Customer', default=_get_customer, readonly=True)
    plot_product_id = fields.Many2one('product.product', string='Product/Plot')
    property_installment_id = fields.Many2one('product.installment.config', string='Property Installment')
    
    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        res.need_property_ref = order.need_property_ref
        for line in res.invoice_line_ids:
            line.preoperty_ref_id = self.preoperty_ref_id.id
            line.property_installment_id = self.property_installment_id.id
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if res:
            res.update({"preoperty_ref_id": self.preoperty_ref_id.id, "property_installment_id":self.property_installment_id.id})
        return res
    
#     account_no = fields.Char(string='Property Reference', readonly=True, copy=False)
    preoperty_ref_id = fields.Many2one('sale.property.reference', string='Property Reference', readonly=False, copy=False)
    property_installment_id = fields.Many2one('product.installment.config', string='Property Installment')
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_agent = fields.Boolean(string='Is Agent', default=False)

class SalePropertyReference(models.Model):
    _name = 'sale.property.reference'
    
    name = fields.Char(string='Property Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    need_property_ref = fields.Boolean(string='Need Property Ref', help='Tick this box if sales order needs property reference on sales order line.', copy=True, default=True, readonly=True)
    agent_id = fields.Many2one('sales.agent')
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    preoperty_ref_id = fields.Many2one('sale.property.reference', string='Property Reference', readonly=False, copy=False)
    property_installment_id = fields.Many2one('product.installment.config', string='Property Installment')
 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: