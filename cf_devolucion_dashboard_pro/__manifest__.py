{
    "name": "CF - Dashboard de Devoluciones PRO",
    "summary": "Cuadro de mando de devoluciones con KPIs, gráficos y cron seguro.",
    "version": "17.0.1.0.0",
    "author": "CosladaFon (CF)",
    "license": "LGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/dashboard_views.xml",
        "data/cron_set_fecha_devolucion.xml"
    ],
    "installable": True,
    "application": False
}
