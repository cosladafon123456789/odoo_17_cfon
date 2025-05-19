# -*- coding: utf-8 -*-

import io
import markupsafe

from odoo.osv import expression
from odoo import models, fields, _
from odoo.tools.misc import formatLang, format_date, xlsxwriter
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class SpanishGenericBookReportCustomHandler(models.AbstractModel):
    _inherit = 'l10n_es.generic.book.es.report.handler'

    def _get_custom_filter(self, moves):
        new_moves = super(SpanishGenericBookReportCustomHandler, self)._get_custom_filter(moves)

        for move in moves:
            if move.is_rebu: 
                new_moves += move

        return new_moves

    def _prepare_data_invoices(self, moves):
        data = []

        book = self.env['sii.map']._get_current_map()

        re_taxes_ids = book._get_group_taxes(self._get_type_book(), ['SRE'])
        bi_taxes_ids = book._get_group_taxes(self._get_type_book(), ['SFRBI'])
        isp_taxes_ids = book._get_group_taxes(self._get_type_book(), ['SFRISP'])
        nd_taxes_ids = book._get_group_taxes(self._get_type_book(), ['SFRND'])

        # My data will be all lines compounded by moves and inside will be another payment lines linked with my move
        for move in moves:

            # Since Odoo skip 0 tax first we should get all taxes
            group_tax_ids = self.env['account.tax.group']
            recharge_links =  {}

            line_with_taxes = move.line_ids.filtered(lambda x: x.tax_ids) 
            for l in line_with_taxes:
                for t in l.tax_ids.filtered(lambda x: x not in re_taxes_ids):
                    if t.tax_group_id and t.tax_group_id not in group_tax_ids:
                        group_tax_ids += t.tax_group_id

                    # Search for recharge
                    for r in l.tax_ids.filtered(lambda x: x in re_taxes_ids):
                        recharge_links.update({t.id: r.id})

            # Insert custom group for REBU
            if move.is_rebu:
                group_tax_ids += self.env.ref('account.%d_tax_group_iva_0' % move.company_id.id, raise_if_not_found=False)

            # Basic fields
            exercise = move.invoice_date.year
            period = self._get_period_from_time(move.invoice_date)
            if move.l10n_es_reports_operation_date:
                exercise = move.l10n_es_reports_operation_date.year
                period = self._get_period_from_time(move.l10n_es_reports_operation_date)

            activity_code, activity_type, activity_group = '', '', ''

            if move.activity:
                activity_code, activity_type, activity_group = self._split_activity(move.activity)
            else:
                if move.journal_id and move.journal_id.activity:
                    activity_code, activity_type, activity_group = self._split_activity(move.journal_id.activity)
                else:
                    if move.company_id and move.company_id.activity:
                        activity_code, activity_type, activity_group = self._split_activity(move.company_id.activity)

            later_deductible = move.later_deductible and "S" or "N"
            deductible_exercise = move.later_deductible_date and move.later_deductible_date.year or ""
            deductible_period = move.later_deductible_date and self._get_period_from_time(move.later_deductible_date) or ""

            country_code = ""
            vat = ""
            if move.partner_id:
                if move.partner_id.country_id:
                    country_code = move.partner_id.country_id.code

                if move.partner_id.vat:
                    possible_country_code = move.partner_id.vat[0:2]
                    exist = self.env['res.country'].search([('code', '=', possible_country_code)])
                    if exist:
                        vat = move.partner_id.vat[2:]
                        if not country_code:
                            country_code = possible_country_code
                    else:
                        vat = move.partner_id.vat

            billing_agreement_registration = ""
            if move.journal_id and move.journal_id.billing_agreement_registration:
                billing_agreement_registration = move.journal_id.billing_agreement_registration
            else:
                if move.company_id and move.company_id.billing_agreement_registration:
                    billing_agreement_registration = move.company_id.billing_agreement_registration

            group_lines = []
            for group in group_tax_ids:

                amount_total, amount_base, amount_tax_type, amount_tax = 0, 0, 0, 0
                recharge_type, recharge_tax = 0, 0
                deductible_vat = 0

                tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id and line.tax_line_id.tax_group_id and line.tax_line_id.tax_group_id.id == group.id)

                operation_clasification = ""
                operation_exent = ""
                investment_goods = ""
                invest_passive_subject = ""
                should_expect_exempt = False
                should_expect_diffrent_rule = False

                if move.is_rebu:
                    operation_clasification = "S1"


                if tax_lines:
                    for tax_line in tax_lines:

                        amount_base += self._get_formatted_sign(self._get_type_book(), move.move_type, 'base', tax_line.tax_base_amount)
                        amount_tax += self._get_formatted_sign(self._get_type_book(), move.move_type, 'balance', tax_line.balance)
                        amount_tax_type = tax_line.tax_line_id.amount

                        if tax_line.tax_line_id in bi_taxes_ids:
                            investment_goods = "S"

                        if tax_line.tax_line_id in isp_taxes_ids:
                            invest_passive_subject = "S"

                        # Check for any recharge linked
                        if recharge_links.get(tax_line.tax_line_id.id, False):
                            recharge_id = recharge_links.get(tax_line.tax_line_id.id, False)
                            recharge_tax_line = move.line_ids.filtered(lambda line: line.tax_line_id and line.tax_line_id.id == recharge_id)

                            recharge_type = recharge_tax_line.tax_line_id.amount
                            recharge_tax = self._get_formatted_sign(self._get_type_book(), move.move_type, 'balance', recharge_tax_line.balance)

                        # Check for operations
                        invoice_map_line_id = book._get_map_line_id(self._get_type_book(), tax_line.tax_line_id)
                        if invoice_map_line_id and invoice_map_line_id.operation_type_id:
                            if invoice_map_line_id.operation_type_id.code != 'EX':
                                operation_clasification =  invoice_map_line_id.operation_type_id.code
                                if invoice_map_line_id.operation_type_id.code == 'N2':
                                    should_expect_diffrent_rule = True
                            else:
                                should_expect_exempt = True
                                operation_exent = invoice_map_line_id.cause_exemption_id and invoice_map_line_id.cause_exemption_id.code or ""

                else:
                    # If we don't have any lines means that is a 0 tax, we should implement so.
                    tax_lines = move.line_ids.filtered(lambda line: line.tax_ids and any([t for t in line.tax_ids if t.tax_group_id and t.tax_group_id.id == group.id]))

                    for tax_line in tax_lines:
                        amount_base += self._get_formatted_sign(self._get_type_book(), move.move_type, 'balance', tax_line.balance)


                        for tax_id in tax_line.tax_ids:
                            # Check for operations
                            invoice_map_line_id = book._get_map_line_id(self._get_type_book(), tax_id)
                            if invoice_map_line_id and invoice_map_line_id.operation_type_id:
                                if invoice_map_line_id.operation_type_id.code != 'EX':
                                    operation_clasification =  invoice_map_line_id.operation_type_id.code
                                    if invoice_map_line_id.operation_type_id.code == 'N2':
                                        should_expect_diffrent_rule = True
                                else:
                                    should_expect_exempt = True
                                    operation_exent = invoice_map_line_id.cause_exemption_id and invoice_map_line_id.cause_exemption_id.code or ""
                
                amount_total = amount_base + amount_tax + recharge_tax

                if move.is_rebu:
                    amount_total = move.amount_total

                deductible_vat = amount_tax
                for tax_line in move.line_ids.filtered(lambda line: line.tax_line_id and line.tax_line_id in nd_taxes_ids):
                    deductible_vat = deductible_vat - self._get_formatted_sign(self._get_type_book(), move.move_type, 'balance', tax_line.balance)

                if should_expect_exempt:
                    # Search if we have any product with exempt
                    exempts = [ml.product_id.product_tmpl_id.cause_exemption_id.code for ml in move.line_ids.filtered(lambda x: x.tax_ids) if ml.product_id and ml.product_id.product_tmpl_id.cause_exemption_id]
                    if exempts:
                        operation_exent = exempts[0]

                if should_expect_diffrent_rule:
                    # Search if is diffrent rule
                    not_subject = [ml.product_id.product_tmpl_id.operation_type_id.code for ml in move.line_ids.filtered(lambda x: x.tax_ids) if ml.product_id and ml.product_id.product_tmpl_id.operation_type_id]
                    if not_subject:
                        operation_clasification = not_subject[0]

                if move.sii_reg_key_id and move.sii_reg_key_id.code:
                    if move.sii_reg_key_id.code in ['02', '08']:
                        investment_goods = "N"
                    if move.sii_reg_key_id.code in ['07', '08', '09']:
                        invest_passive_subject = "N"
                    if move.sii_reg_key_id.code in ['03', '05']:
                        deductible_vat = 0
                if move.sii_invoice_type_id and move.sii_invoice_type_id.code:
                    if move.sii_invoice_type_id.code in ['F5', 'LC']:
                        invest_passive_subject = "N"
                
                group_lines.append({
                    'operation_key': move.sii_reg_key_id and move.sii_reg_key_id.code or '',
                    'operation_clasification': operation_clasification,
                    'investment_goods': investment_goods,
                    'invest_passive_subject': invest_passive_subject,
                    'later_deductible': later_deductible,
                    'deductible_exercise': deductible_exercise,
                    'deductible_period': deductible_period,
                    'operation_exent': operation_exent,
                    'total_invoice': amount_total,
                    'amount_base': amount_base,
                    'tax_type': amount_tax_type,
                    'deductible_vat': deductible_vat,
                    'charged_vat': amount_tax,
                    'recharge_type': recharge_type,
                    'recharged_vat': recharge_tax,
                })

            payment_lines = []
            payments = self.env['account.payment']
            if move.invoice_payments_widget:
                contents = move.invoice_payments_widget.get("content", [])
                for content in contents:
                    if content.get("account_payment_id", False):
                        payments += self.env['account.payment'].browse(content.get("account_payment_id"))

            for payment in payments:
                bank_account_id = ''
                if payment.method_used and payment.method_used == '05':
                    try:
                        mandate = getattr(move, 'sdd_mandate_id')
                        if mandate:
                            bank_account = mandate.partner_bank_id and mandate.partner_bank_id.acc_number or ''
                            bank_account_id = str(bank_account.replace(' ', ''))
                        else:
                            refund_invoice_ids = self.env['account.move'].search([('reversed_entry_id', '=', move.id)])
                            for refund_invoice_id in refund_invoice_ids:
                                mandate = getattr(refund_invoice_id, 'sdd_mandate_id')
                                if mandate:
                                    bank_account = mandate.partner_bank_id and mandate.partner_bank_id.acc_number or ''
                                    bank_account_id = str(bank_account.replace(' ', ''))
                        if not mandate and payment.partner_bank_id:
                            bank_account = payment.partner_bank_id and payment.partner_bank_id.acc_number or ''
                            bank_account_id = str(bank_account.replace(' ', ''))
                    except Exception as e:
                        pass

                if not bank_account_id:
                    if payment.journal_id:
                        bank_account_id = str(payment.journal_id.name)

                recieve_exercise = payment.date.year
                recieve_period = self._get_period_from_time(payment.date)

                payment_lines.append({
                    'exercise': recieve_exercise,
                    'period': recieve_period,
                    'recieve_date': payment.date or '',
                    'recieve_amount': payment.amount,
                    'recieve_method_used': payment.method_used or '',
                    'recieve_id_method_used': bank_account_id or '',
                })


            data.append({
                'exercise': exercise,
                'period': period,
                'activity_code': activity_code,
                'activity_type': activity_type,
                'activity_group': activity_group,
                'invoice_type': move.sii_invoice_type_id and move.sii_invoice_type_id.code or '',
                'concept': '',
                'compute_income': 0,
                'compute_deductible': 0,
                'expedition_date': move.invoice_date or '',
                'operation_date': move.l10n_es_reports_operation_date or '',
                'serie': '',
                'number': move.name or '',
                'final_number': '',
                'reception_date': move.date or '',
                'reception_number': move.ref or '',
                'reception_final_number': '',
                'type_identification': move.partner_id and move.partner_id.l10n_es_reports_documentation_type or '',
                'country_code': country_code,
                'identification': vat,
                'name': move.partner_id and move.partner_id.name or '',
                #'operation_key': move.sii_reg_key_id and move.sii_reg_key_id.code or '',
                #'operation_clasification': operation_clasification,
                #'operation_exent': operation_exent,
                #'total_invoice': '',
                #'amount_base': '',
                #'tax_type': '',
                #'charged_vat': '',
                #'recharge_type': '',
                #'recharged_vat': '',
                'grouped_lines': group_lines,
                #'recieve_date': '',
                #'recieve_amount': '',
                #'recieve_method_used': '',
                #'recieve_id_method_used': '',
                'payment_lines': payment_lines,
                'irpf_income_tax_type': 0,
                'irpf_income_tax_amount': 0,
                'billing_agreement_registration': billing_agreement_registration or '',
                'property_situation': move.property_situations_id and move.property_situations_id.code or '',
                'property_cadastral_reference': move.cadastral_reference or '',
                'external_reference': str(move.id),
            })

        return data