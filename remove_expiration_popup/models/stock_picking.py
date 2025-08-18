from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_expiration_date(self):
        """
        Override del control de caducidad a nivel de picking.
        Si Odoo llama a este método para mostrar el popup de caducidad,
        devolvemos siempre True para que no se bloquee ni aparezca el aviso.
        """
        return True

    def button_validate(self):
        """
        Forzamos el contexto para ignorar cualquier comprobación de caducidad
        que dependiera de flags de contexto.
        """
        return super(StockPicking, self.with_context(ignore_expiration=True)).button_validate()