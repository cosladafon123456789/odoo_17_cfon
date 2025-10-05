{
    "name": "CF - Dashboard de Devoluciones",
    "summary": "Cuadro de mando con KPIs y gráficos (motivos, interno/externo, evolución mensual). Añade fecha de devolución.",
    "version": "17.0.1.0.0",
    "author": "CosladaFon (CF)",
    "license": "LGPL-3",
    "depends": ["sale_management", "cf_devolucion_motivos_corrected"],
    "data": [
        "security/ir.model.access.csv",
        "views/dashboard_views.xml"
    ],
    "installable": true,
    "application": false
}