from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CustomeSaleOrder(models.Model):
    _name = 'custome.sale.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Custom Sale Order Backlist'
    _order = 'id desc'


    name = fields.Char(string='Name',copy=False, readonly=True, default='New')
    start_date = fields.Datetime(string="Start Date",copy=False)
    end_date = fields.Datetime(string="End Date",copy=False)
    sale_order_ids = fields.One2many('sale.order','custome_sale_id', string="Sale Order")
    sale_picking_done = fields.Float(string='Sale picking Done', compute='_compute_sale_picking_done', store=True)
    picking_ids = fields.One2many('stock.picking','custome_order_id',string='Stock Picking')
    state = fields.Selection([
    ('draft', 'Draft'),
    ('start_date', 'Start'),
    ('end_date', 'End'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False,)
    sale_order_count = fields.Integer(string="Sale Order Count",compute="_compute_sale_order_count")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('custome.sale.order') or 'New'
        return super(CustomeSaleOrder, self).create(vals)


    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_start_date(self):
        for rec in self:
            rec.start_date = fields.Datetime.now()
            rec.state = 'start_date'

    def action_end_date(self):
        for rec in self:
            rec.end_date = fields.Datetime.now()
            rec.state = 'end_date'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    
    @api.depends('start_date', 'end_date')
    def _compute_sale_picking_done(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                delta = rec.end_date - rec.start_date
                rec.sale_picking_done = delta.total_seconds()
            else:
                rec.sale_picking_done = 0.0



    def action_process(self):
        for rec in self:
            end_time = rec.start_date + timedelta(seconds=rec.sale_picking_done)

            done_moves = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('picking_type_id.code', '=', 'outgoing'),
                ('date', '>=', rec.start_date),
                ('date', '<=', end_time),
            ])
            related_orders = done_moves.mapped('picking_id.sale_id').filtered(lambda so: so)

            related_pickings = done_moves.mapped('picking_id').filtered(lambda p: p.state == 'done')

            rec.sale_order_ids = [(6, 0, related_orders.ids)]
            related_pickings.write({'custome_order_id': rec.id})

            rec.state = 'done'

    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = [('id', 'in', self.sale_order_ids.ids)]
        return action


    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)