{
    "name": "Truncar mensajes largos (carga diferida, seguro)",
    "summary": "Colapsa mensajes >N caracteres con <details>/<summary> y 'Ver más/menos'",
    "version": "17.0.1.0.0",
    "category": "Discuss",
    "license": "LGPL-3",
    "author": "Cosladafon + ChatGPT",
    "depends": ["mail", "web"],
    "data": [
        "data/ir_config_parameter.xml"
    ],
    "assets": {
        "web.assets_backend_lazy": [
            "mail_message_truncate_lazy/static/src/js/truncate_lazy.js",
            "mail_message_truncate_lazy/static/src/scss/truncate_lazy.scss",
        ]
    },
    "installable": True,
    "application": False
}
