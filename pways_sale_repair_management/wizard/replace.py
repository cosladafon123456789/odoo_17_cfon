from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class ReplaceOrderWizard(models.TransientModel):
    _name = 'replace.order.wizard'
    _description = "Replace order Wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    dest_location_id = fields.Many2one('stock.location', 'Replace Location', domain=[("usage", "=", "internal")])
    line_ids = fields.One2many('replace.order.line.wizard', 'replace_order_id', string="Products")
   
   
    def action_replace_order(self):
        """In Order"""
        stock_picking_model = self.env['stock.picking']
        active_id = self.env.context.get('active_id')
        sale = self.env['sale.order'].browse(active_id)

        # --- Incoming Picking (In Order) ---
        incoming = stock_picking_model.search(
            [('sale_id', '=', sale.id)],
            limit=1
        )
        if not incoming:
            raise ValueError("No matching incoming picking found for the sale order.")
        incoming.ensure_one()

        picking_type_in = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming')], limit=1
        )
        if not picking_type_in or not picking_type_in.sequence_id:
            raise ValueError("Incoming picking type or sequence is not properly configured.")

        for line in sale.order_line.filtered('create_repair_order'):
            line_data = [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': incoming.location_dest_id.id,
                'location_dest_id': self.dest_location_id.id,
                'name': line.product_id.name,
                'sale_line_id': line.id,
            })]
            vals_in = {
                'sale_id': sale.id,
                'origin': sale.name,
                'move_ids_without_package': line_data,
                'partner_id': sale.partner_id.id,
                'location_id': incoming.location_dest_id.id,
                'location_dest_id': self.dest_location_id.id,
                'picking_type_id': picking_type_in.id,
            }
            in_order = stock_picking_model.create(vals_in)
            # message_rec = self.env['mail.message'].sudo().create({
            # "message_type": 'comment', 
            # 'model': 'sale.order',
            # 'res_id': sale.id, 
            # "body": _('Order Successfully Replaced IN Order %s',in_order.name)
            # })
            msg_body = _('Order Successfully Replaced IN Order %s',in_order.name)
            sale.message_post(body=msg_body)

        # --- Outgoing Picking (OUt Order) ---
        outgoing = stock_picking_model.search(
            [('sale_id', '=', sale.id)],
            limit=1
        )
        if not outgoing:
            raise ValueError("No matching outgoing picking found for the sale order.")
        outgoing.ensure_one()

        picking_type_out = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing')], limit=1
        )
        if not picking_type_out or not picking_type_out.sequence_id:
            raise ValueError("Outgoing picking type or sequence is not properly configured.")

        for line in sale.order_line.filtered('create_repair_order'):
            for line_product in self.line_ids.product_id:
                line_data = [(0, 0, {
                    'product_id': line_product.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': self.dest_location_id.id,
                    'location_dest_id': outgoing.location_dest_id.id,
                    'name': line_product.name,
                    'sale_line_id': line.id,
                })]
                vals_out = {
                    'sale_id': sale.id,
                    'origin': sale.name,
                    'move_ids_without_package': line_data,
                    'partner_id': sale.partner_id.id,
                    'location_id': self.dest_location_id.id,
                    'location_dest_id': outgoing.location_dest_id.id,
                    'picking_type_id': picking_type_out.id,
                }
            out_order = stock_picking_model.create(vals_out)
            # message_rec = self.env['mail.message'].sudo().create({
            # "message_type": 'comment', 
            # 'model': 'sale.order', 
            # 'res_id': sale.id, 
            # "body": _('Order Successfully Replaced Out Order %s',out_order.name)
            # })
            msg_body = _('Order Successfully Replaced Out Order %s',out_order.name)
            sale.message_post(body=msg_body)

        return True

class ReplaceOrderLineWizard(models.TransientModel):
    _name = 'replace.order.line.wizard'
    _description = "Replace order Wizard"
    
    replace_order_id = fields.Many2one('replace.order.wizard')
    product_id = fields.Many2one('product.product', string="Product")

        
class ReturnOrderWizard(models.TransientModel):
    _name = 'return.order.wizard'
    _description = "Return order Wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    dest_location_id = fields.Many2one('stock.location', 'Return Location', domain=[("usage", "=", "internal")])

    def action_return_order(self):
        """In Order"""
        stock_picking_model = self.env['stock.picking']
        active_id = self.env.context.get('active_id')
        sale = self.env['sale.order'].browse(active_id)

        # --- Incoming Picking (In Order) ---
        incoming = stock_picking_model.search(
            [('sale_id', '=', sale.id)],
            limit=1
        )
        if not incoming:
            raise ValueError("No matching incoming picking found for the sale order.")
        incoming.ensure_one()

        picking_type_in = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming')], limit=1
        )
        if not picking_type_in or not picking_type_in.sequence_id:
            raise ValueError("Incoming picking type or sequence is not properly configured.")

        for line in sale.order_line.filtered('create_repair_order'):
            line_data = [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': incoming.location_dest_id.id,
                'location_dest_id': self.dest_location_id.id,
                'name': line.product_id.name,
                'sale_line_id': line.id,
            })]
            vals = {
                'sale_id': sale.id,
                'origin': sale.name,
                'move_ids_without_package': line_data,
                'partner_id': sale.partner_id.id,
                'location_id': incoming.location_dest_id.id,
                'location_dest_id': self.dest_location_id.id,
                'picking_type_id': picking_type_in.id,
            }
            out_order = stock_picking_model.create(vals)
            # message_rec = self.env['mail.message'].sudo().create({
            # "message_type": 'comment', 
            # 'model': 'sale.order', 
            # 'res_id': sale.id, 
            # "body": _('Order Successfully Returned Out Order %s',out_order.name)
            # })
            msg_body = _('Order Successfully Returned Out Order %s',out_order.name)
            sale.message_post(body=msg_body)
        
        return True