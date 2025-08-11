{
    "name": "Clamp mensajes (CSS solo, seguro)",
    "summary": "Limita visualmente los mensajes largos en Conversaciones/Chatter con line-clamp (sin JS).",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "author": "Cosladafon + ChatGPT",
    "depends": ["mail", "web"],
    "assets": {
        "web.assets_backend": [
            "mail_message_clamp_css/static/src/scss/clamp.scss"
        ]
    },
    "installable": True,
    "application": False
}
