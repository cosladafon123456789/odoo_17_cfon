# ©  2008-now Terrabit
# See README.rst file on addons root folder for license details

from odoo import _, http
from odoo.http import request

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.mail import _message_post_helper


class CustomerPortal(portal.CustomerPortal):
    @http.route()
    def portal_quote_decline(self, order_id, access_token=None, decline_message=None, **kwargs):
        res = super().portal_quote_decline(
            order_id, access_token=access_token, decline_message=decline_message, **kwargs
        )
        if "cant_reject" in res.location and "cancel_requested" in kwargs:
            order_sudo = self._document_check_access("sale.order", order_id, access_token=access_token)
            message = decline_message
            order_sudo.set_to_cancel(message)
            message = _("Cancellation requested by user. Reason: %s") % message
            _message_post_helper("sale.order", order_id, message, **{"token": access_token} if access_token else {})
            return request.redirect(order_sudo.get_portal_url())

        return res
