from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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

    latest_delivery_date = fields.Date(
        string='Latest Delivery Date (Till Today)',
        compute='_compute_latest_delivery_date',
        store=True
    )

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