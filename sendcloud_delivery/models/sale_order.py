from odoo import fields,api,models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sb_service_point_details = fields.Text('Service Point Details', help='Stored response of sendcloud service point when user select service point from front end.')

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for record in self.filtered(lambda x : x.sb_service_point_details):
            for picking in record.mapped('picking_ids'):
                picking.write({'sb_service_point_details' : record.sb_service_point_details})
        return res
