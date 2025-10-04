{
    "name": "CF - Motivos de Devolución (Wizard + Informes)",
    "summary": "Wizard en botón 'Recibido' para registrar motivo, detalle (texto largo) y tipo de error (Interno/Externo) + informes pivot/gráfico.",
    "version": "17.0.1.0.0",
    "author": "CosladaFon (CF)",
    "license": "LGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/devolucion_wizard_views.xml",
        "views/devolucion_report_views.xml"
    ],
    "installable": True,
    "application": False,
}