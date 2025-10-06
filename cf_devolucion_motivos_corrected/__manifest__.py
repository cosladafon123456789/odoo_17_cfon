{
    "name": "CF - Forzar Wizard de Devolución",
    "summary": "Abre un wizard obligatorio de motivo de devolución al pulsar el botón 'Recibido' en pedidos de venta.",
    "version": "17.0.1.0.0",
    "author": "CosladaFon (CF)",
    "website": "https://www.cosladafon.com",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": [
        "sale_management",
        "pways_sale_repair_management"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/devolucion_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "description": """
Módulo personalizado de CosladaFon (CF)
--------------------------------------
- Muestra un wizard al pulsar el botón "Recibido" en las órdenes de venta.
- Permite seleccionar motivo, tipo de error y detalle de la devolución.
- Ejecuta la acción original tras confirmar el wizard.
""",
}
