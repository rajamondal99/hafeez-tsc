# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class ProductInstallmentConfig(models.Model):
    _name = 'product.installment.config'
    _description = 'Product Installment Config'
    
    
    @api.depends('total_sale_price', 'total_number_installment')
    def _get_monthly_installment(self):
        for installment in self:
            if installment.total_number_installment > 0:
                installment.monthly_installment = installment.total_sale_price / installment.total_number_installment

    @api.onchange('total_number_installment')
    def onchange_debit_account_id(self):
        if self.total_number_installment == 0:
            self.total_sale_price = self.product_id.lst_price
        
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Installment Name', required=True)
    total_sale_price = fields.Float(string='Sales Price', required=True)
    total_number_installment = fields.Integer(string='Number of Installment', required=True)
    agent_commision = fields.Float(string='Marketer Commission(%)', required=False)
    monthly_installment = fields.Float(compute="_get_monthly_installment",
                                       string="Monthly Installment",
                                       store=True)
    allow_commision = fields.Boolean('Allow Commission', default=True)

    @api.onchange('allow_commision')
    def onchange_allow_commision(self):
        for line in self:
            if line.allow_commision is False:
                line.agent_commision = False
     
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    estate_code = fields.Char('Estate Code', readonly=True)
    is_estate = fields.Boolean('Is an Estate')

    @api.model
    def create(self, vals):
        if vals.get('is_estate', False):
            vals.update(estate_code = self.env['ir.sequence'].next_by_code('estate.code') or '/')
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('is_estate', False) and not rec.estate_code:
                vals.update(estate_code = self.env['ir.sequence'].next_by_code('estate.code') or '/')
        return super(ProductTemplate, self).write(vals)


class Product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        if vals.get('lst_price', False):
            installment = self.env['product.installment.config'].search([('product_id', 'in', self.ids), ('total_number_installment', '=', 0.0)], limit=1)
            if installment:
                installment.total_sale_price = vals['lst_price']
        return super(Product, self).write(vals)
    
    intallment_ids = fields.One2many('product.installment.config', 'product_id', copy=True)

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
