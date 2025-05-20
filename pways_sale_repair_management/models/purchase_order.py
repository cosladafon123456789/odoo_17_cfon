# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from collections import defaultdict
from odoo.exceptions import ValidationError
from datetime import date
from datetime import timedelta


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    warranty_period = fields.Selection(
        [('30', '30 Days'), ('60', '60 Days'), ('90', '90 Days')],
        string='Warranty Period',
        # compute='_compute_warranty_period',
        store=True
    )
    warranty_expiry_date = fields.Date(
        string='Expiry Date',
        compute='_compute_warranty_expiry',
        store=True
    )

    # @api.depends('partner_id', 'partner_id.warranty_period')
    # def _compute_warranty_period(self):
    #     for po in self:
    #         po.warranty_period = po.partner_id.warranty_period

    @api.depends('warranty_period', 'date_order')
    def _compute_warranty_expiry(self):
        for po in self:
            if po.warranty_period and po.date_order:
                days = int(po.warranty_period)
                # date_order is a datetime; convert to date if needed
                order_date = fields.Date.to_date(po.date_order)
                po.warranty_expiry_date = order_date + timedelta(days=days)
            else:
                po.warranty_expiry_date = False


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    expiry_date = fields.Date(related='order_id.warranty_expiry_date')


    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        self._check_orderpoint_picking_type()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.product_id.display_name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (self.orderpoint_id and not (self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': product.description_pickingin or self.name,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'product_packaging_id': self.product_packaging_id.id,
            'sequence': self.sequence,
            'date_force_expiry': self.expiry_date
        }