from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError
from odoo.addons.hr_holidays_contract.models.hr_contract import HrContract


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    is_probation = fields.Boolean(string="Probation")
    probation_start_date = fields.Date(default=date.today(), string="Probation Start Date")
    probation_end_date = fields.Date(string="Probation End Date")
    state = fields.Selection([
        ('draft', 'New'),
        ('wait_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
        ('reject','Rejected'),
    ], string='Status', group_expand=True, copy=False,
        tracking=True, help='Status of the contract', default='draft')

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'
        return True

    def action_open(self):
        # self.write({'state': 'open'})
        for rec in self:
            rec.state = 'open'
        return True

    def action_wait_approval(self):
        for rec in self:
            rec.state = 'wait_approval'
        return True

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
        return True

    def action_close(self):
        for rec in self:
            rec.state = 'close'
        return True

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
        return True

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'
        return True

    def write(self, vals):
        print("......write....")
        # Special case when setting a contract as running:
        # If there is already a validated time off over another contract
        # with a different schedule, split the time off, before the
        # _check_contracts raises an issue.
        # If there are existing leaves that are spanned by this new
        # contract, update their resource calendar to the current one.
        if not (vals.get("state") == 'open' or vals.get('kanban_state') == 'done'):
            return super().write(vals)

        specific_contracts = self.env['hr.contract']
        all_new_leave_origin = []
        all_new_leave_vals = []
        leaves_state = {}
        # In case a validation error is thrown due to holiday creation with the new resource calendar (which can
        # increase their duration), we catch this error to display a more meaningful error message.
        try:
            for contract in self:
                if vals.get('state') != 'open' and contract.state != 'draft':
                    # In case the current contract is not in the draft state, the kanban_state transition does not
                    # cause any leave changes.
                    continue
                leaves = contract._get_leaves()
                sort_order = {
                    'draft': 1,
                    'wait_approval': 2,
                    'approved': 3,
                    'open': 4,
                    'close': 5,
                    'cancel': 6,
                    'reject': 7,
                }
                for leave in leaves:
                    # Get all overlapping contracts but exclude draft contracts that are not included in this transaction.
                    overlapping_contracts = leave._get_overlapping_contracts(contract_states=[
                        ('state', '!=', 'cancel'),
                        ('resource_calendar_id', '!=', False),
                        '|', '|', ('id', 'in', self.ids),
                                  ('state', '!=', 'draft'),
                             ('kanban_state', '=', 'done'),
                    ]).sorted(key=lambda c: sort_order[c.state])
                    if len(overlapping_contracts.resource_calendar_id) <= 1:
                        if overlapping_contracts and leave.resource_calendar_id != overlapping_contracts[0].resource_calendar_id:
                            leave.resource_calendar_id = overlapping_contracts[0].resource_calendar_id
                        continue
                    if leave.id not in leaves_state:
                        leaves_state[leave.id] = leave.state
                    if leave.state != 'refuse':
                        leave.action_refuse()
                    super(HrContract, contract).write(vals)
                    specific_contracts += contract
                    for overlapping_contract in overlapping_contracts:
                        new_request_date_from = max(leave.request_date_from, overlapping_contract.date_start)
                        new_request_date_to = min(leave.request_date_to, overlapping_contract.date_end or date.max)
                        new_leave_vals = leave.copy_data({
                            'request_date_from': new_request_date_from,
                            'request_date_to': new_request_date_to,
                            'state': leaves_state[leave.id],
                        })[0]
                        new_leave = self.env['hr.leave'].new(new_leave_vals)
                        new_leave._compute_date_from_to()
                        new_leave._compute_duration()
                        # Could happen for part-time contract, that time off is not necessary
                        # anymore.
                        if new_leave.date_from < new_leave.date_to:
                            all_new_leave_origin.append(leave)
                            all_new_leave_vals.append(new_leave._convert_to_write(new_leave._cache))
            if all_new_leave_vals:
                new_leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    leave_skip_state_check=True
                ).create(all_new_leave_vals)
                new_leaves.filtered(lambda l: l.state in 'validate')._validate_leave_request()
                for index, new_leave in enumerate(new_leaves):
                    new_leave.message_post_with_source(
                        'mail.message_origin_link',
                        render_values={'self': new_leave, 'origin': all_new_leave_origin[index]},
                        subtype_xmlid='mail.mt_note',
                    )
        except ValidationError:
            raise ValidationError(_("Changing the contract on this employee changes their working schedule in a period "
                                    "they already took leaves. Changing this working schedule changes the duration of "
                                    "these leaves in such a way the employee no longer has the required allocation for "
                                    "them. Please review these leaves and/or allocations before changing the contract."))
        return super(HrContract, self - specific_contracts).write(vals)
