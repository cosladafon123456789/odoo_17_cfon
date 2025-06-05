from odoo import api, fields, models, _


class LotQuantityWizard(models.TransientModel):
	_name = 'lot.quantity.wizard'
	_description = "Lot Quantity Wizard"

	product_id = fields.Many2one('product.product', string="Product")
	line_ids = fields.One2many('lot.quantity.line.wizard', 'wizard_id', string="Lots")

	# @api.model
	# def default_get(self, fields):
	# 	res = super().default_get(fields)
	# 	product_id = self.env.context.get('default_product_id')
	# 	if product_id:
	# 		move_lines = self.env['stock.move.line'].search([
	# 			('product_id', '=', product_id),
	# 			('lot_id', '!=', False),
	# 			('state', '=', 'done'),
	# 		])
	# 		res['line_ids'] = [(0, 0, {
	# 			'lot_id': ml.lot_id.id,
	# 			'quantity': ml.quantity,
	# 		}) for ml in move_lines]
	# 	return res


class LotQuantityLineWizard(models.TransientModel):
	_name = 'lot.quantity.line.wizard'
	_description = "Lot Quantity Line Wizard"

	wizard_id = fields.Many2one('lot.quantity.wizard', string="Wizard")
	lot_id = fields.Many2one('stock.lot', string="Lot")
	quantity = fields.Float(string="Quantity")
