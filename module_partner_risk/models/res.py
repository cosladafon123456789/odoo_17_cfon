# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class InsuranceCarrier(models.Model):
    _name = 'insurance.carrier'

    name = fields.Char('Nombre')
    partner_id = fields.Many2one('res.partner','Contacto')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    risk_caution   = fields.Boolean(string=_("Credit and Caution"), default=False)
    risk_credit    = fields.Float(string=_("Risk Credit"), default=0.0, tracking=True)
    risk_level     = fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),
                                    ('5', '5'),('6', '6'),('7', '7'),('8', '8'),
                                    ('9', '9'),('10', '10'),], string=_("Risk Level"))
    state          = fields.Selection([('active', _('Active')),('locked', _('Locked'))], string=_("State"), default='active')
    risk_available = fields.Float(string=_("Credit Available"), compute='get_risk_available',default=0.0)
    
    risk_company_id   = fields.Many2one('insurance.carrier', _('Insurance Carrier'))

    has_groups = fields.Boolean(string=_("Has Groups"), compute="_compute_has_groups")

    def get_risk_available(self):
        _logger.info("")
        _logger.info("    - - - -- - - - estoy calculando el riesgo")
        _logger.info("")
        for r in self:
            parent_id = r._get_parent_id()
            _logger.info("que es el parent_id")
            _logger.info(parent_id)
            all_orders = r.env['sale.order'].sudo().search([('partner_id', 'child_of', [parent_id.id]), ('state', 'in', ('sale', 'done'))])
            all_invoices = r.env['account.move'].sudo().search([('partner_id', 'child_of', [parent_id.id]), ('state', '=', 'posted'), ('move_type', 'in', ('out_invoice', 'out_refund'))])
            _logger.info("cuales son los pedidos asociados")
            _logger.info(all_orders)

            if all_orders:            
                total_amount = sum([order.amount_total for order in all_orders])
                _logger.info("cuando dinero lleva")
                _logger.info(total_amount)
                total_amount_paid = 0
                for order in all_orders:
                    _logger.info("para cada pedido")
                    _logger.info(order)
                    _logger.info(order.state)
                    #_logger.info(invoice.move_type)
                    #_logger.info(invoice.payment_ids)
                    if order.invoice_status == 'invoiced':
                        for invoice in order.invoice_ids:
                            if invoice.payment_state == 'reversed':
                                _logger.info("revertida")
                                _logger.info("la mini resta")
                                _logger.info(invoice.amount_total - invoice.amount_residual)
                                total_amount_paid -= invoice.amount_total - invoice.amount_residual
                            elif invoice.payment_state == 'paid' or invoice.payment_state == 'partial':
                                _logger.info("pagado o parcial")
                                total_amount_paid += invoice.amount_total - invoice.amount_residual
                                #original total_amount_paid += invoice.amount_total

                _logger.info("actualmente tiene pagado ")
                _logger.info(total_amount_paid)
                total_amount_unpaid = total_amount - total_amount_paid
                _logger.info("le queda por pagar")
                _logger.info(total_amount_unpaid)
                if total_amount_unpaid > parent_id.risk_credit:
                    r.risk_available = 0
                else:
                    r.risk_available = r.risk_credit - total_amount_unpaid
                    _logger.info("riesgo disponible")
                    _logger.info(r.risk_credit - total_amount_unpaid)
            else:
                r.risk_available = r.risk_credit
    ###################################################################################

    def _compute_has_groups(self):
        for r in self:
            r.has_groups = r.user_has_groups('module_partner_risk.partner_risk_security') or r.user_has_groups('base.group_system')
    
    @api.constrains('state')
    def _check_state(self):
        for r in self:
            if r.risk_caution and (not r.risk_level or r.risk_credit == 0 or r.risk_credit < 0) and r.state == 'active':
                raise ValidationError(_("First fill the fields: risk level and risk credit in order to change the state of partner."))

    @api.model
    def _get_parent_id(self):
        LIMIT_RECURSION = 100
        partner = self
        stillHaveParent = True
        errorTooMuchParents = False
        i = 0
        if self.parent_id:
            while(stillHaveParent and not errorTooMuchParents):
                if not partner.parent_id:
                    stillHaveParent = False
                else:
                    partner = partner.parent_id
                if i == LIMIT_RECURSION:
                    errorTooMuchParents = True
                i += 1
            if errorTooMuchParents:
                raise UserError(_("Partner have too much hiperarchy!"))

        return partner

    @api.model
    def _check_risk(self, amount_unpaid):
        available_credit = self.risk_available
        _logger.info("el contacto tiene aun disponible")
        _logger.info(available_credit)
        _logger.info("el pedido tiene un importe de")
        _logger.info(amount_unpaid)
        if available_credit < amount_unpaid:
            return True
        return False
        #parent_id = self._get_parent_id()
        #all_orders = self.env['sale.order'].sudo().search([('partner_id', 'child_of', [parent_id.id]), ('state', 'in', ('sale', 'done'))])
        #if all_orders:            
        #    total_amount = sum([order.amount_total for order in all_orders])
        #    total_amount_paid = 0
        #    for order in all_orders:
        #        if order.invoice_status == 'invoiced':
        #            for invoice in order.invoice_ids:
        #                if invoice.state == 'paid':
        #                    total_amount_paid += invoice.amount_total

        #    total_amount_unpaid = total_amount - total_amount_paid
        #    if total_amount_unpaid > parent_id.risk_credit:
        #        return True
        #return False

    @api.model
    def _check_caution(self):
        parent_id = self._get_parent_id()
        return parent_id.risk_caution
