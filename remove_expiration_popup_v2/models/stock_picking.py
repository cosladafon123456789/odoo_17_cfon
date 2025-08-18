from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_expiration_date(self):
        """
        Algunos flujos de validación llaman a este método para mostrar el popup
        de caducidad. Si existe, devolvemos True para que no bloquee.
        """
        return True

    def button_validate(self):
        """
        Añadimos un flag de contexto para saltarse comprobaciones de caducidad
        en otros métodos que miran el contexto.
        """
        return super(StockPicking, self.with_context(ignore_expiration=True)).button_validate()