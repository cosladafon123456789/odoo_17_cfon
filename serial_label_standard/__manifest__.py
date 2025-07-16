{
    "name": "Etiqueta de N° de Serie (Estándar)",
    "version": "1.0",
    "depends": ["stock"],
    "author": "ChatGPT",
    "category": "Inventory",
    "description": "Imprime una etiqueta con el número de serie del producto (sin campos personalizados).",
    "data": [
        "report/serial_label_report.xml",
        "report/serial_label_template.xml",
        "views/stock_lot_view.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": False
}
