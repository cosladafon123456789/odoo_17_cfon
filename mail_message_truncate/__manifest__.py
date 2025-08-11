{
    "name": "Truncar mensajes largos en Conversaciones",
    "summary": "Oculta mensajes >500 caracteres con '… Ver más' y expande al hacer clic",
    "version": "17.0.1.0.0",
    "category": "Discuss",
    "license": "LGPL-3",
    "author": "Cosladafon + ChatGPT",
    "depends": ["mail", "web"],
    "assets": {
        "web.assets_backend": [
            "mail_message_truncate/static/src/js/truncate_messages.js",
            "mail_message_truncate/static/src/scss/truncate_messages.scss",
        ]
    },
    "installable": True,
    "application": False,
}
