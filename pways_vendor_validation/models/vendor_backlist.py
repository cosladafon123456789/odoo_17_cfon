from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class VendorBacklist(models.Model):
    _name = 'vendor.backlist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', copy=False, readonly=True, default='New')
    vendor_id = fields.Many2many('res.partner',string='Vendor Name', required=True,)
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date')
    state = fields.Selection([
    ('draft', 'Draft'),
    ('approve', 'Approved'),
    ('reject', 'Rejected'),
    ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False,)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.backlist') or 'New'
        return super(VendorBacklist, self).create(vals)
    

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_approve(self):
        for rec in self:
            # Check if any other record is already approved
            existing_approved = self.search([
                ('state', '=', 'approve'),
                ('id', '!=', rec.id),
            ], limit=1)
            if existing_approved:
                raise ValidationError(_(
                    "Another record (%s) is already in 'Approved' state. "
                    "Only one blacklist record can be approved at a time."
                ) % existing_approved.name)

            rec.state = 'approve'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_id_blacklist_warning(self):
        if self.partner_id:
            today = fields.Date.today()
            blacklisted = self.env['vendor.backlist'].search([
                ('vendor_id', 'in', self.partner_id.ids),
                ('state', '=', 'approve'),
                ('start_date', '<=', today),
                '|',
                ('end_date', '=', False),
                ('end_date', '>=', today),
            ], limit=1)
            if blacklisted:
                return {
                    'warning': {
                        'title': _("Blacklisted Vendor"),
                        'message': _("Vendor '%s' is blacklisted (Ref: %s) as of today. You should not use this vendor.")
                                   % (self.partner_id.name, blacklisted.name),
                    }
                }



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    latest_delivery_date = fields.Datetime(
        string='Latest Delivery Date (Till Today)',
        compute='_compute_latest_delivery_date',
        store=True
    )
    order_minutes = fields.Float(
        string='Order Minutes',
        compute='_compute_order_minutes',
        search='_search_order_minutes')
    picking_user_id = fields.Many2one(
        'res.users',
        string='Picking Done By',
        compute='_compute_picking_done_user',
        store=True
    )

    @api.depends('picking_ids.state')
    def _compute_picking_done_user(self):
        for order in self:
            # Find the first done picking for this sale order
            done_pickings = order.picking_ids.filtered(lambda p: p.state == 'done')
            if done_pickings:
                # Get the user who validated the first done picking (write_uid)
                order.picking_user_id = done_pickings[0].write_uid
            else:
                order.picking_user_id = False

    
    @api.depends('order_line.move_ids.date')
    def _compute_latest_delivery_date(self):
        today = fields.Date.today()
        for order in self:
            latest_date = False
            for line in order.order_line:
                # Filter moves that are 'done' and done on or before today
                moves = line.move_ids.filtered(lambda m: m.date and m.state == 'done' and m.date.date() <= today)
                move_dates = [move.date.date() for move in moves]
                if move_dates:
                    max_date = max(move_dates)
                    if not latest_date or max_date > latest_date:
                        latest_date = max_date
            order.latest_delivery_date = latest_date


    @api.depends('order_line.move_ids.date', 'order_line.move_ids.state')
    def _compute_order_minutes(self):
        now = fields.Datetime.now()
        for order in self:
            # Get all done moves and their dates
            done_moves = order.order_line.mapped('move_ids').filtered(lambda m: m.state == 'done' and m.date)
            if done_moves:
                # Use the latest done move date
                latest_done_date = max(done_moves.mapped('date'))
                delta = now - latest_done_date
                order.order_minutes = delta.total_seconds() / 60.0
            else:
                order.order_minutes = 0.0

    def _search_order_minutes(self, operator, value):
        """
        Search for sale orders whose latest done delivery (stock move) happened
        within the specified minutes.
        """
        now = fields.Datetime.now()
        target_datetime = now - timedelta(minutes=value)

        # Reverse operator to use on 'move_ids.date'
        reverse_map = {
            '<=': '>=',
            '<':  '>',
            '>=': '<=',
            '>':  '<',
            '=':  '=',
            '!=': '!=',
        }

        move_date_operator = reverse_map.get(operator)
        if not move_date_operator:
            raise ValueError(f"Unsupported operator for order_minutes: {operator}")

        # Domain to find sale orders with at least one `done` move
        return [
            ('order_line.move_ids.state', '=', 'done'),
            ('order_line.move_ids.date', move_date_operator, target_datetime)
        ]


    # @api.depends('order_line.move_ids.date')
    # def _compute_order_minutes(self):
    #     now = fields.Datetime.now()
    #     for order in self:
    #         if order.create_date:
    #             delta = now - order.create_date
    #             order.order_minutes = delta.total_seconds() / 60
    #         else:
    #             order.order_minutes = 0.0


    # def _search_order_minutes(self, operator, value):
    #     """ Search on computed field 'order_minutes' """
    #     # Calculate the corresponding create_date based on 'value' minutes ago
    #     now = fields.Datetime.now()
    #     target_datetime = now - timedelta(minutes=value)

    #     # Reverse operator: since we're searching 'order_minutes <= 30',
    #     # we search 'create_date >= now - 30 minutes'
    #     reverse_map = {
    #         '<=': '>=',
    #         '<':  '>',
    #         '>=': '<=',
    #         '>':  '<',
    #         '=':  '=',
    #         '!=': '!=',
    #     }

    #     create_date_operator = reverse_map.get(operator)
    #     if not create_date_operator:
    #         raise ValueError(f"Unsupported operator for order_minutes: {operator}")

    #     return [('create_date', create_date_operator, target_datetime)]