from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    helpdesk_ticket_count = fields.Integer(
        string="Tickets Helpdesk",
        compute="_compute_helpdesk_ticket_count"
    )

    @api.depends('name')
    def _compute_helpdesk_ticket_count(self):
        for order in self:
            tickets = self.env['helpdesk.ticket'].search_count([
                ('name', 'ilike', order.name)
            ])
            order.helpdesk_ticket_count = tickets

    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tickets Helpdesk',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form',
            'domain': [('name', 'ilike', self.name)],
            'context': dict(self.env.context, default_name=self.name),
        }
