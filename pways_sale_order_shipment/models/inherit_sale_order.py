from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_rebu = fields.Boolean(string='Es REBU')


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    imei_ids = fields.Many2many('stock.lot',string='IMEI Number', copy=False, domain="[('product_id', '=', product_id)]")
    tracking_number = fields.Char(string='Tracking Number')
    picking_status = fields.Char(string="Shipping status", compute='_compute_picking_status', store=False)
    source_id = fields.Many2one('utm.source',related="order_id.source_id",string="Channel (WEB)")
    amount_total = fields.Monetary(related="order_id.amount_total",string='Total')
    invoice_status = fields.Selection(related="order_id.invoice_status",string='Invoice Status')
    date_order = fields.Datetime(related="order_id.date_order", string="Order Date")
    is_validated = fields.Boolean(string='Validated')
    carrier_id = fields.Many2one('delivery.carrier',string='Transporista')
    is_rebu = fields.Boolean(related="order_id.is_rebu",string='Es REBU')

    @api.depends('order_id.picking_ids.state')
    def _compute_picking_status(self):
        state_mapping = {
            'draft': 'Draft',
            'waiting': 'Waiting Another Operation',
            'confirmed': 'Waiting',
            'assigned': 'Ready',
            'done': 'Done',
            'cancel': 'Cancelled'
        }

        for line in self:
            pickings = line.order_id.picking_ids
            if pickings:
                states = [state_mapping.get(pick.state, pick.state) for pick in pickings]
                line.picking_status = ', '.join(states)
            else:
                line.picking_status = 'No Pickings'



    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        if self.imei_ids:
            vals["imei_ids"] = self.imei_ids.ids
        return vals


    def action_validation(self):
        for line in self:

            if line.is_validated:
                raise ValidationError("This line has already validated.")

            if not line.imei_ids:
                raise ValidationError("Please assign IMEI numbers before validating this line.")
            
            order = line.order_id

            if order.state != 'sale':
                order.action_confirm()

            related_moves = line.move_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
            for move in related_moves:
                picking = move.picking_id
                if picking.state in ('done', 'cancel'):
                    continue

                move.imei_ids = [(6, 0, line.imei_ids.ids)]

                move.move_line_ids.unlink()
                move._action_assign()
                
                if line.carrier_id:
                    picking.carrier_id = line.carrier_id
                
                if line.tracking_number:
                    picking.carrier_tracking_ref = line.tracking_number
            
            line.is_validated = True
        
        return self.env.ref('pways_sale_order_shipment.report_imei_label_action').report_action(self)


class StockMove(models.Model):
    _inherit = 'stock.move'

    imei_ids = fields.Many2many('stock.lot',string='Serial Numbers', domain="[('product_id', '=', product_id)]")

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        vals["imei_ids"] = self.imei_ids.ids
        return vals

   

    def _action_assign(self):
        skip_moves = self.env['stock.move']
        res = super(StockMove, self)._action_assign()
        for move in self:
            if move.imei_ids:
                skip_moves |= move
                move.move_line_ids.unlink()
                
                for imei in move.imei_ids:
                    move_line_vals = move._prepare_move_line_vals()
                    move_line_vals['lot_id'] = imei.id

                    move_line_vals['quantity'] = 1

                    move_line = self.env['stock.move.line'].create(move_line_vals)
        return res




class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        fields = super()._get_custom_move_fields()
        fields += ["imei_ids"]
        return fields