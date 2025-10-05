{
    "name": "CF - Dashboard de Devoluciones (SAFE)",
    "summary": "Cuadro de mando con KPIs y gráficos seguro (sin dependencias duras). Añade fecha_devolucion y usa los campos de motivos si existen.",
    "version": "17.0.1.0.0",
    "author": "CosladaFon (CF)",
    "license": "LGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/dashboard_views.xml",
        "data/cron_set_fecha_devolucion.xml"
    ],
    "installable": true,
    "application": false
}