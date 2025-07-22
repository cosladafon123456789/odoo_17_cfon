from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_final_rating = fields.Selection([
        ('1', '★☆☆☆☆'),
        ('2', '★★☆☆☆'),
        ('3', '★★★☆☆'),
        ('4', '★★★★☆'),
        ('5', '★★★★★'),
    ], string="Last Evaluation")

    def action_open_vendor_evaluation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Evaluations',
            'view_mode': 'form',
            'res_model': 'vendor.evaluation',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
            'target': 'current',
        }



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_final_rating = fields.Selection([
        ('1', '★☆☆☆☆'),
        ('2', '★★☆☆☆'),
        ('3', '★★★☆☆'),
        ('4', '★★★★☆'),
        ('5', '★★★★★'),
    ], string='Vendor Rating', related='partner_id.vendor_final_rating', readonly=True, store=True)