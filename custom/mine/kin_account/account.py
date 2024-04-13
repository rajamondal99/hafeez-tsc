# -*- coding: utf-8 -*-


from openerp import api, fields, models, _



class AccountJournalExtend(models.Model):
    _inherit = "account.journal"


    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account', help='This helps to automatically populate the invoices with the set analytic account')



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    # @api.one  # The @api.one calls the methods for as many items in the account.invoice.line, however a for loop can be used inside the method as well to achieve thesame purpose
    # @api.depends('selling_price', 'balance')
    # def _profit_loss(self):
    #     self.ensure_one()
    #     self.profit_loss = self.selling_price + self.balance
    #
    # #is_sales_invoice = fields.Boolean(string = "Is Sales Invoice")
    # selling_price = fields.Monetary(string="Selling Price")
    # profit_loss = fields.Monetary(string="Profit/Loss",compute='_profit_loss',store=True)
