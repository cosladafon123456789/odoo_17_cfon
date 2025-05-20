# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from collections import defaultdict
from odoo.exceptions import ValidationError
from datetime import date
from datetime import timedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    repair_check_count = fields.Integer(string="Count", compute="_compute_repair_check_count")
    replace_count = fields.Integer(string="Replace Count", compute="_compute_replace_count")
    delivery_check = fields.Boolean("Check Delivery", compute='_compute_delivery_check')
    delivery_done = fields.Boolean('Delivery Done', default=False)
    is_warranty = fields.Boolean('Warranty')
    warranty_period = fields.Selection(
        [('30', '30 Days'), ('60', '60 Days'), ('90', '90 Days')],
        string='Warranty Period',
        store=True)
    warranty_expiry_date = fields.Date(
        string='Expiry Date',
        compute='_compute_warranty_expiry',
        store=True)

    @api.depends('warranty_period', 'date_order')
    def _compute_warranty_expiry(self):
        for po in self:
            if po.warranty_period and po.date_order:
                days = int(po.warranty_period)
                order_date = fields.Date.to_date(po.date_order)
                po.warranty_expiry_date = order_date + timedelta(days=days)
            else:
                po.warranty_expiry_date = False

    def button_recieved(self):
        self.delivery_done = True
        return True

    # def button_replace(self):
    #     has_create_repair_order = any(line.create_repair_order for line in self.order_line)
    #     if not has_create_repair_order:
    #         raise ValidationError("No lines are selected to create replace order.")
    #     action = self.env["ir.actions.actions"]._for_xml_id("pways_sale_repair_management.create_replace_order_action")
    #     msg_body = _('Order Successfully Replaced.')
    #     self.message_post(body=msg_body)
    #     return action

    def button_replace(self):
        self.ensure_one()
        repair_lines = self.order_line.filtered(lambda l: l.create_repair_order)
        
        if not repair_lines:
            raise ValidationError("No lines are selected to create replace order.")
        
        wizard = self.env['replace.order.wizard'].create({
        })
        
        for line in repair_lines:
            self.env['replace.order.line.wizard'].create({
                'replace_order_id': wizard.id,
                'product_id': line.product_id.id,
            })

        return {
            'name': 'Create Replace Order',
            'type': 'ir.actions.act_window',
            'res_model': 'replace.order.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def _prepare_default_reversal(self, move):
        reverse_date = date.today()
        account_data = self.env['account.move'].search([('invoice_origin', '=', self.name),('move_type', '=', 'out_invoice')])
        mixed_payment_term = move.invoice_payment_term_id.id if move.invoice_payment_term_id.early_pay_discount_computation == 'mixed' else None
        return {
            'ref': _('Reversal of: %(move_name)s, (Refund)', move_name=move.name),
            'date': reverse_date,
            'invoice_date_due': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (reverse_date or move.date) or False,
            'journal_id': account_data.journal_id.id,
            'invoice_payment_term_id': mixed_payment_term,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': 'at_date' if reverse_date > fields.Date.context_today(self) else 'no',
        }

    def reverse_moves(self, is_modify=False):
        self.ensure_one()
        moves = self.invoice_ids

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = default_vals.get('auto_post') != 'no'
            is_cancel_needed = not is_auto_post and is_modify
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)
            moves._message_log_batch(
                bodies={move.id: _('This entry has been %s', reverse._get_html_link(title=_("reversed"))) for move, reverse in zip(moves, new_moves)}
            )

            if is_modify:
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data({'date': reverse_date})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)

            moves_to_redirect |= new_moves

        # self.new_move_ids = moves_to_redirect

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(moves_to_redirect) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': moves_to_redirect.id,
                'context': {'default_move_type':  moves_to_redirect.move_type},
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves_to_redirect.ids)],
            })
            if len(set(moves_to_redirect.mapped('move_type'))) == 1:
                action['context'] = {'default_move_type':  moves_to_redirect.mapped('move_type').pop()}
        msg_body = _('Customer Credit Note Created.')
        self.message_post(body=msg_body)
        return action
    
    def button_refund(self):
        self.reverse_moves()
        has_create_repair_order = any(line.create_repair_order for line in self.order_line)
        if not has_create_repair_order:
            raise ValidationError("No lines are selected to create return order.")
        action = self.env["ir.actions.actions"]._for_xml_id("pways_sale_repair_management.pways_create_return_order_action")
        return action
    
    def action_return_to_customer(self):
        """In Order"""
        stock_picking_model = self.env['stock.picking']

        so_picking_id = stock_picking_model.search(
            [('sale_id', '=', self.id)],
            limit=1
        )

        # --- Incoming Picking (In Order) ---
        picking_type_in = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming')], limit=1)
    
        for line in self.order_line.filtered('create_repair_order'):
            line_data = [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': so_picking_id.location_dest_id.id,
                'location_dest_id': so_picking_id.location_id.id,
                'name': line.product_id.name,
                'sale_line_id': line.id,
            })]
            vals_in = {
                'sale_id': self.id,
                'origin': self.name,
                'move_ids_without_package': line_data,
                'partner_id': self.partner_id.id,
                'location_id': so_picking_id.location_dest_id.id,
                'location_dest_id': so_picking_id.location_id.id,
                'picking_type_id': picking_type_in.id,
                'group_id': self.procurement_group_id.id,
            }
            print('vals_in////////////',vals_in)
            print("Self ><><><><>>>>>>>>>>>>>>>>",self.name)
            in_order = stock_picking_model.create(vals_in)
            if self.procurement_group_id:
                in_order.write({'group_id': self.procurement_group_id.id})
            print(in_order.group_id.id)
            msg_body = _('Order Successfully Returned to Customer IN Order %s',in_order.name)
            self.message_post(body=msg_body)
            
        # --- Outgoing Picking (OUt Order) ---
        picking_type_out = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing')], limit=1)
        for line in self.order_line.filtered('create_repair_order'):
            line_data = [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': so_picking_id.location_id.id,
                'location_dest_id': so_picking_id.location_dest_id.id,
                'name': line.product_id.name,
                'sale_line_id': line.id,
            })]
            vals_out = {
                'sale_id': self.id,
                'origin': self.name,
                'move_ids_without_package': line_data,
                'partner_id': self.partner_id.id,
                'location_id': so_picking_id.location_id.id,
                'location_dest_id': so_picking_id.location_dest_id.id,
                'picking_type_id': picking_type_out.id,
                'group_id': self.procurement_group_id.id,
            }
            print('vals_out\\\\\\\\\\\\\\',vals_out)
            out_order = stock_picking_model.create(vals_out)
            if self.procurement_group_id:
                out_order.write({'group_id': self.procurement_group_id.id})
            print(out_order.group_id.id)
            msg_body = _('Order Successfully Returned to Customer Out Order %s',out_order.name)
            self.message_post(body=msg_body)
            print('called  action------------->>>>>')
            
        return True
    

    def button_return_to_customer(self):
        self.action_return_to_customer()
        return True

    def action_rma(self):
        stock_picking_model = self.env['stock.picking']

        so_picking_id = stock_picking_model.search(
            [('sale_id', '=', self.id)],limit=1)

        rma_location = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1).rma_location

        if not rma_location:
            raise ValidationError(_("You need to fill RMA Location in Warehouse"))

        if self.warranty_expiry_date >= date.today():
            print("Warranty is valid. Proceeding with operation.")
        else:
            raise ValidationError("Your warranty period is over.")

        picking_type_in = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming')], limit=1)
    
        for line in self.order_line.filtered('create_repair_order'):
            line_data = [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': so_picking_id.location_dest_id.id,
                'location_dest_id': rma_location.id,
                'name': line.product_id.name,
                'sale_line_id': line.id,
            })]
            vals_in = {
                'sale_id': self.id,
                'origin': self.name,
                'move_ids_without_package': line_data,
                'partner_id': self.partner_id.id,
                'location_id': so_picking_id.location_dest_id.id,
                'location_dest_id': rma_location.id,
                'picking_type_id': picking_type_in.id,
                'group_id': self.procurement_group_id.id,
            }
            print('vals_in////////////',vals_in)
            print("Self ><><><><>>>>>>>>>>>>>>>>",self.name)
            in_order = stock_picking_model.create(vals_in)
            if self.procurement_group_id:
                in_order.write({'group_id': self.procurement_group_id.id})
            print(in_order.group_id.id)
            msg_body = _('Your Products are in Warranty, Sent Successfully to RMA %s',in_order.name)
            self.message_post(body=msg_body)
        return True

    def button_rma(self):
        self.action_rma()
        return True

    def _compute_delivery_check(self):
        for rec in self:
            delivery_check = False  # Default value

            receipts = self.env['stock.picking'].search([('sale_id', '=', rec.id)])
            account = self.env['account.move'].search([('invoice_origin', '=', rec.name),('move_type', '=', 'out_invoice')])

            if receipts and all(p.state == 'done' for p in receipts):
                if account:
                    if account and all(inv.amount_residual == 0 for inv in account):
                        delivery_check = True

            rec.delivery_check = delivery_check


    def button_create_repair_order(self):
        has_create_repair_order = any(line.create_repair_order for line in self.order_line)
        if not has_create_repair_order:
            raise ValidationError("No lines are selected to create repair order.")

        action = self.env["ir.actions.actions"]._for_xml_id("pways_sale_repair_management.create_repair_order_action")
        return action

    def button_view_rapir_orders(self):
        activities = self.env['repair.order'].sudo().search([('sale_order_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("repair.action_repair_order_tree")
        action['domain'] = [('id', 'in', activities.ids)]
        return action

    def _compute_repair_check_count(self):
        count_of_repair = self.env['repair.order'].search_count([('sale_order_id', '=', self.id)])
        self.repair_check_count = count_of_repair

    def button_view_replace_orders(self):
        activities = self.env['stock.picking'].sudo().search([('replace_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("stock.view_picking_form")
        action['domain'] = [('id', 'in', activities.ids)]
        return action

    def _compute_replace_count(self):
        count_of_repair = self.env['stock.picking'].search_count([('replace_id', '=', self.id)])
        self.replace_count = count_of_repair

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    create_repair_order = fields.Boolean(string="Repair" , copy=False)
    


