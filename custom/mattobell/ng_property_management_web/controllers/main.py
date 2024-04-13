import openerp
from openerp import SUPERUSER_ID

from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale

class website_sale(website_sale):
    
    #fully overridden from base for insert sales agents
    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sale order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        cr, uid, context = request.cr, request.uid, request.context
        payment_obj = request.registry.get('payment.acquirer')
        sale_order_obj = request.registry.get('sale.order')

        order = request.website.sale_get_order(context=context)

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        shipping_partner_id = False
        if order:
            if order.partner_shipping_id.id:
                shipping_partner_id = order.partner_shipping_id.id
            else:
                shipping_partner_id = order.partner_invoice_id.id

        values = {
            'website_sale_order': order
        }
        values['errors'] = sale_order_obj._get_errors(cr, uid, order, context=context)
        values.update(sale_order_obj._get_website_data(cr, uid, order, context))
        if not values['errors']:
            # find an already existing transaction
            tx = request.website.sale_get_transaction()
            acquirer_ids = payment_obj.search(cr, SUPERUSER_ID, [('website_published', '=', True), ('company_id', '=', order.company_id.id)], context=context)
            values['acquirers'] = list(payment_obj.browse(cr, uid, acquirer_ids, context=context))
            render_ctx = dict(context, submit_class='btn btn-primary', submit_txt=_('Pay Now'))
            for acquirer in values['acquirers']:
                acquirer.button = payment_obj.render(
                    cr, SUPERUSER_ID, acquirer.id,
                    tx and tx.reference or request.env['payment.transaction'].get_next_reference(order.name),
                    order.amount_total,
                    order.pricelist_id.currency_id.id,
                    values={
                        'return_url': '/shop/payment/validate',
                        'partner_id': shipping_partner_id,
                        'billing_partner_id': order.partner_invoice_id.id,
                    },
                    context=render_ctx)
                
        sale_agent_ids = request.registry.get('sales.agent').search(cr, uid, [], order='agent_name ASC')#probuse
        sale_agents = request.registry.get('sales.agent').browse(cr, uid, sale_agent_ids)#probuse
        
        branch_ids = request.registry.get('branch.branch').search(cr, uid, [], order='code ASC')#probuse
        branches = request.registry.get('branch.branch').browse(cr, uid, branch_ids)#probuse
        
        values.update({'sale_agents': sale_agents,
                       'branches': branches})#probuse
        return request.website.render("website_sale.payment", values)
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id), add_qty=float(add_qty), set_qty=float(set_qty), **kw)
        return request.redirect("/shop/cart")

    @http.route('/shop/payment/sale_agent', type='json', auth="public", website=True, csrf=False)
    def payment_sale_agent(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        order = request.website.sale_get_order(context=context)
        if post.get('sale_agent', False):
            sale_agent = post.get('sale_agent', False)
            branch = post.get('branch', False)
            request.registry['sale.order'].write(
                cr, SUPERUSER_ID, [order.id], {
                    'agent_id': int(sale_agent),
                    'branch_id': int(branch),
                }, context=context)
        return
    
    @http.route('/shop/get_installments', type='json', auth="public", website=True, csrf=False)
    def get_installments(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        installment_list = []
        product_id = post.get('product_id')
        product = request.registry.get('product.product').browse(cr, uid, product_id)#probuse
        for installment in product.intallment_ids:
            installment_list.append({'id': installment.id,
                                     'name' : installment.name,
                                     'amount': installment.total_sale_price,
                                     'installment_no': installment.total_number_installment})
        return installment_list
    
    