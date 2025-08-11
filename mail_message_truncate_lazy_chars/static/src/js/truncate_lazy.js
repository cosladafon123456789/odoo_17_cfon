\
/** @odoo-module **/
/**
 * Truncado ultra-seguro para Odoo 17:
 * - Carga en web.assets_backend_lazy (no bloquea startup).
 * - Usa <details>/<summary> nativo para expandir/colapsar.
 * - Protegido con try/catch y checks defensivos.
 * - No altera lógica de Odoo; solo envuelve el cuerpo del mensaje.
 */

import { registry } from "@web/core/registry";
import { session } from "@web/session";

const svc = {
    name: "cf_truncate_lazy_service",
    async start(env) {
        // Cargar umbral desde ir.config_parameter (si falla, usar 500)
        let THRESHOLD = 500;
        try {
            const rpc = env.services.rpc || (await import("@web/core/network/rpc_service"));
            const getParam = async (key, defV) => {
                try {
                    const val = await env.services.orm.call(
                        "ir.config_parameter",
                        "get_param",
                        [key, String(defV)]
                    );
                    const num = parseInt(val, 10);
                    return Number.isFinite(num) ? num : defV;
                } catch {
                    return defV;
                }
            };
            THRESHOLD = await getParam("mail_message_truncate.threshold", 500);
        } catch {
            // dejar 500
        }

        const SELECTOR_MSG = ".o-mail-Message";
        const BODY_CANDIDATES = [
            ".o-mail-Message-content",
            ".o-mail-Message-body",
            ".o-mail-Message__body",
            "[data-message-body]",
            ".o-mail-Message *[data-oe-type='html']",
        ];

        function findBodyEl(msgEl) {
            for (const sel of BODY_CANDIDATES) {
                const el = msgEl.querySelector?.(sel);
                if (el) return el;
            }
            return null;
        }

        function makeWrapper(bodyEl, threshold) {
            // Evitar doble wrap
            if (bodyEl.closest?.(".cf-details-wrap")) return null;

            const textLen = (bodyEl.textContent || "").trim().length;
            if (textLen <= threshold) return null;

            const details = document.createElement("details");
            details.className = "cf-details-wrap";
            details.open = false;

            const summary = document.createElement("summary");
            summary.className = "cf-summary";
            summary.textContent = "… Ver más";

            const contentWrap = document.createElement("div");
            contentWrap.className = "cf-content";

            // Mover el cuerpo original dentro del contentWrap
            // Clonamos el nodo para no romper refs; luego ocultamos el original
            // más seguro: movemos los hijos
            while (bodyEl.firstChild) {
                contentWrap.appendChild(bodyEl.firstChild);
            }

            details.appendChild(summary);
            details.appendChild(contentWrap);

            // Insertar el details dentro de bodyEl y marcar
            bodyEl.appendChild(details);
            bodyEl.classList.add("cf-truncated-ready");

            // Cambiar texto de summary al abrir/cerrar
            details.addEventListener("toggle", () => {
                try {
                    summary.textContent = details.open ? "Ver menos" : "… Ver más";
                } catch {}
            });

            return details;
        }

        function process(root) {
            try {
                root.querySelectorAll?.(SELECTOR_MSG)?.forEach((msg) => {
                    try {
                        const body = findBodyEl(msg);
                        if (!body) return;
                        makeWrapper(body, THRESHOLD);
                    } catch {}
                });
            } catch {}
        }

        // Procesar cuando el DOM ya está en pantalla
        queueMicrotask(() => {
            try {
                process(document);
                // Observer muy ligero, solo para nuevos mensajes en pantalla
                const obs = new MutationObserver((mut) => {
                    for (const m of mut) {
                        for (const n of m.addedNodes || []) {
                            if (!(n instanceof HTMLElement)) continue;
                            if (n.matches?.(SELECTOR_MSG)) {
                                const body = findBodyEl(n);
                                if (body) makeWrapper(body, THRESHOLD);
                            } else {
                                process(n);
                            }
                        }
                    }
                });
                obs.observe(document.body, { childList: true, subtree: true });
            } catch {}
        });

        return {};
    },
};

registry.category("services").add("cf_truncate_lazy_service", svc);
