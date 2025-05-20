# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from collections import defaultdict
from odoo.exceptions import ValidationError
from datetime import date
from datetime import timedelta



class StockPicking(models.Model):
    _inherit = "stock.picking"

    replace_id = fields.Many2one('sale.order')
    sale_order_count = fields.Integer(string="Sale order", compute="_compute_sale_order_view_count")
    repair_order_count = fields.Integer(string="Repair Order", compute="_compute_repair_order_view_count")
    # expiry_date = fields.Date(related='purchase_id.warranty_expiry_date')

    def button_view_sale_order(self):
        activities = self.env['sale.order'].sudo().search([('id', '=', self.sale_id.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('id', 'in', activities.ids)]
        return action

    def _compute_sale_order_view_count(self):
        activities = self.env['sale.order'].sudo().search_count([('id', '=', self.sale_id.id)])
        self.sale_order_count = activities

    def button_view_repair_order(self):
        activities = self.env['repair.order'].sudo().search([('sale_order_id', '=', self.sale_id.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("repair.action_repair_order_tree")
        action['domain'] = [('id', 'in', activities.ids)]
        return action

    def _compute_repair_order_view_count(self):
        activities = self.env['sale.order'].sudo().search_count([('id', '=', self.sale_id.id)])
        self.repair_order_count = activities


class StockWarehouseInherit(models.Model):
    _inherit = "stock.warehouse"

    rma_location = fields.Many2one('stock.location', string="RMA Location")

class RepairOrder(models.Model):
    _inherit = "repair.order"

    sale_order_line_id = fields.Many2one('sale.order.line', string="Picking" , copy=False)
    picking_count = fields.Integer(string="Count", compute="_compute_button_view_count")

    def button_view_picking(self):
        activities = self.env['stock.picking'].sudo().search([('sale_id', '=', self.sale_order_id.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['domain'] = [('id', 'in', activities.ids)]
        return action

    def _compute_button_view_count(self):
        count_of_picking = self.env['stock.picking'].sudo().search_count([('sale_id', '=', self.sale_order_id.id)])
        self.picking_count = count_of_picking


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    warranty_period = fields.Selection(
        [('30', '30 Days'), ('60', '60 Days'), ('90', '90 Days')],
        string='Warranty Period')

