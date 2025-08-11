{
    "name": "Truncar mensajes largos (super seguro, 50 chars)",
    "summary": "Colapsa mensajes largos en Conversaciones y Chatter con … Ver más / Ver menos",
    "version": "17.0.1.1.0",
    "license": "LGPL-3",
    "author": "Cosladafon + ChatGPT",
    "depends": ["mail", "web"],
    "assets": {
        "web.assets_backend": [
            "mail_message_truncate_super_safe/static/src/js/truncate_super_safe.js",
            "mail_message_truncate_super_safe/static/src/scss/truncate_super_safe.scss",
        ]
    },
    "installable": True,
    "application": False
}
