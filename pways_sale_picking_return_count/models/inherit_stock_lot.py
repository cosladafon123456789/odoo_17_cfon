from odoo import fields, models, api
from odoo.exceptions import ValidationError

class StockLot(models.Model):
    _inherit = "stock.lot"

    return_count = fields.Float(string="Return Count",compute="_compute_return_count",store=True, copy=False)
    scrap_count = fields.Integer(string='Scrap Count', compute="_compute_scrap_count",copy=False)
    

    @api.depends("quant_ids.quantity")
    def _compute_return_count(self):
        for lot in self:
            # Only consider quants that have a quantity > 0 (ignore new empty lot)
            if not lot.quant_ids:
                lot.return_count = 0
                continue

            # Get outgoing moves that are done and actually linked to this lot
            outgoing_moves = lot.quant_ids.mapped("product_id").mapped("stock_move_ids").filtered(
                lambda m: m.state == "done"
                and m.picking_id.picking_type_code == "outgoing"
                and lot.id in m.move_line_ids.mapped("lot_id").ids
            )
            # Filter only moves that have returned moves
            returned_moves = outgoing_moves.filtered(lambda m: m.returned_move_ids)

            lot.return_count = len(returned_moves)

            # Trigger mail only when exactly 2
            # if lot.return_count == 2:
            #     lot._notify_return_count_alert()

    def action_open_scrap_wizard(self):
        if self.return_count <= 2:
            raise ValidationError("No available quantity to scrap.")

        return {
            "name": "Scrap Lot/Serial",
            "type": "ir.actions.act_window",
            "res_model": "serial.scrap.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_lot_id": self.id},
        }

    def _compute_scrap_count(self):
        for rec in self:
            scrap_count = self.env['stock.scrap'].search([('lot_id', '=', self.id)])
            rec.scrap_count = len(scrap_count)

    def action_view_scrap(self):
        self.ensure_one()
        request_records = self.env['stock.scrap'].search([('lot_id', '=', self.id)])
        action = {
            'name': 'Scrap',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.scrap',
            'view_mode': 'list,form',
            'domain': [('lot_id', '=', self.id)],
            # 'context': {},
            'target': 'current',
        }
        if len(request_records) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': request_records.id,
            })
        return action
 

    def _get_return_alert_recipients(self):
        """
        Returns the res.partner records of users who should be notified.
        Example: Administrator and some other user group.
        """
        # Example: Send to Administrator and all users in Internal User group
        admin_user = self.env.ref("base.user_admin")  # Administrator
        internal_group = self.env.ref("base.group_user")  # Internal Users group

        users = admin_user | internal_group.users
        return users.mapped("partner_id")

    def _notify_return_count_alert(self):
        template = self.env.ref("pways_sale_picking_return_count.mail_template_return_count_alert",raise_if_not_found=False,)
        if not template:
            return

        for lot in self:
            partners = lot._get_return_alert_recipients()
            if partners:
                template.with_context(recipient_ids=partners.ids).send_mail(lot.id, force_send=True)

    # @api.depends('quant_ids.quantity')
    # def _compute_return_count(self):
    #     print("ttttttttt")
    #     # delivery_ids_by_lot = self._find_delivery_ids_by_lot()
    #     for lot in self:
    #         outgoing_pickings = lot.quant_ids.mapped('product_id').mapped('stock_move_ids').filtered(
    #             lambda p: p.state == "done" and p.picking_code == "outgoing")
    #         # delivery_ids = delivery_ids_by_lot[lot.id]
    #         # brw_delivery_ids = self.env['stock.move'].browse(delivery_ids)
    #         print("fffffffffff", outgoing_pickings)
    #         # for dev in outgoing_pickings:
    #         #     print("devvvvvvvv", dev.reference)

    #         returned_moves = outgoing_pickings.filtered(lambda m: m.returned_move_ids)
    #         print('returned_moves.........................',returned_moves)

    #         lot.return_count = len(returned_moves)
    #         print(f">>> Lot {lot.name} ({lot.id}) => return_count = {lot.return_count}")




class StockPicking(models.Model):
    _inherit = "stock.picking"

    has_serials_with_multiple_returns = fields.Boolean(
        string="Has Serials with 2+ Returns",
        compute="_compute_has_serials_with_multiple_returns"
    )

    def _compute_has_serials_with_multiple_returns(self):
        for picking in self:
            lots = picking.move_line_ids.lot_id
            picking.has_serials_with_multiple_returns = any(
                lot.return_count >= 2 for lot in lots if lot
            )

class StockMove(models.Model):
    _inherit = 'stock.move'

    has_problematic_batches = fields.Boolean(
        string="Has Problematic Batches",
        compute="_compute_has_problematic_batches",
        store=False
    )

    def _compute_has_problematic_batches(self):
        for move in self:
            move.has_problematic_batches = any(
                ml.lot_id and ml.lot_id.return_count >= 2
                for ml in move.move_line_ids
            )


