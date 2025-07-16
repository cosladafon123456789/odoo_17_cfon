{
    "name": "Etiqueta IMEI desde número de serie",
    "version": "1.0",
    "depends": ["stock"],
    "author": "ChatGPT",
    "category": "Inventory",
    "description": "Permite imprimir una etiqueta con IMEI desde el número de serie del producto.",
    "data": [
        "report/serial_label_report.xml",
        "report/serial_label_template.xml",
        "views/stock_lot_view.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": False
}
