# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp import api, fields, models, _, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_is_zero, float_compare


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'



    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                price_unit = line.taxes_id.compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_excluded']
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                price_unit = order.currency_id.with_context(date=line.order_id.date_order or fields.Date.context_today(self)).compute(price_unit, order.company_id.currency_id, round=False)

            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'date': line.order_id.date_order,
                'date_expected': line.date_planned,
                'location_id': line.order_id.partner_id.property_stock_supplier.id,
                'location_dest_id': line.order_id._get_destination_location(),
                'picking_id': picking.id,
                'partner_id': line.order_id.dest_address_id.id,
                'move_dest_id': False,
                'state': 'draft',
                'purchase_line_id': line.id,
                'company_id': line.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.order_id.picking_type_id.id,
                'group_id': line.order_id.group_id.id,
                'procurement_id': False,
                'origin': line.order_id.name,
                'route_ids': line.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in line.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id':line.order_id.picking_type_id.warehouse_id.id,
            }

            # Fullfill all related procurements with this po line
            diff_quantity = line.product_qty
            for procurement in line.procurement_ids:
                procurement_qty = procurement.product_uom._compute_qty_obj(procurement.product_uom, procurement.product_qty, line.product_uom)
                tmp = template.copy()
                tmp.update({
                    'product_uom_qty': min(procurement_qty, diff_quantity),
                    'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                    'procurement_id': procurement.id,
                    'propagate': procurement.rule_id.propagate,
                })
                done += moves.create(tmp)
                diff_quantity -= min(procurement_qty, diff_quantity)
            if float_compare(diff_quantity, 0.0, precision_rounding=line.product_uom.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        return done


    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            self.product_id,
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, self.product_id.supplier_taxes_id, self.taxes_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.with_context(date=self.order_id.date_order or fields.Date.context_today(self)).compute(price_unit, self.order_id.currency_id)

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit, to_uom_id=self.product_uom.id)

        self.price_unit = price_unit
