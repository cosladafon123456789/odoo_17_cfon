# -*- coding: utf-8 -*-
{
    "name": "Sale Blacklist Info",
    "version": "1.5",
    "category": "Sales",
    "summary": "Bloqueo de entregas por lista negra con recordatorio visual de reglas.",
    "author": "CFON Telecomunicaciones",
    "depends": ["base", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_blacklist_views.xml",
    ],
    "installable": True,
    "application": False,
}
