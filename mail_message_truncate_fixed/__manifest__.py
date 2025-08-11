{
    "name": "Truncar mensajes largos en Conversaciones (seguro)",
    "summary": "Colapsa mensajes >500 caracteres con '… Ver más' sin bloquear el webclient",
    "version": "17.0.1.0.1",
    "category": "Discuss",
    "license": "LGPL-3",
    "author": "Cosladafon + ChatGPT",
    "depends": ["mail", "web"],
    "assets": {
        "web.assets_backend": [
            "mail_message_truncate_fixed/static/src/js/truncate_messages_safe.js",
            "mail_message_truncate_fixed/static/src/scss/truncate_messages.scss",
        ]
    },
    "installable": True,
    "application": False,
}
