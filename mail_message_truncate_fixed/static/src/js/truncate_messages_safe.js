\
/** @odoo-module **/
import { registry } from "@web/core/registry";

/**
 * Servicio ligero que, tras cargar el webclient, observa mensajes y
 * colapsa aquellos con más de 500 caracteres. Totalmente defensivo.
 */
const THRESHOLD = 500;

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
    return msgEl;
}

function ensureControls(msgEl, bodyEl) {
    try {
        if (!msgEl || !bodyEl) return;
        if (msgEl.classList.contains("cf-truncated-ready")) return;

        const textLen = (bodyEl.textContent || "").trim().length;
        if (textLen <= THRESHOLD) {
            msgEl.classList.add("cf-truncated-skip");
            return;
        }

        // Controles
        const controls = document.createElement("div");
        controls.className = "cf-truncate-controls";

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn btn-link p-0 cf-toggle-btn";
        btn.textContent = "… Ver más";

        btn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            const expanded = msgEl.classList.toggle("cf-expanded");
            btn.textContent = expanded ? "Ver menos" : "… Ver más";
        });

        const parent = bodyEl.parentElement || bodyEl;
        if (!parent.querySelector(".cf-truncate-controls")) {
            parent.appendChild(controls);
            controls.appendChild(btn);
        }

        msgEl.classList.add("cf-truncated-ready");
        msgEl.classList.remove("cf-expanded");
    } catch (e) {
        // No romper la UI
        // console.warn("ensureControls error", e);
    }
}

function processContainer(root) {
    try {
        root.querySelectorAll?.(".o-mail-Message")?.forEach((msg) => {
            const body = findBodyEl(msg);
            ensureControls(msg, body);
        });
    } catch (e) {
        // console.warn("processContainer error", e);
    }
}

function initObserver(root) {
    const obs = new MutationObserver((mutations) => {
        for (const m of mutations) {
            for (const node of m.addedNodes || []) {
                if (!(node instanceof HTMLElement)) continue;
                if (node.matches?.(".o-mail-Message")) {
                    ensureControls(node, findBodyEl(node));
                } else {
                    processContainer(node);
                }
            }
        }
    });
    obs.observe(root, { childList: true, subtree: true });
    return obs;
}

const service = {
    name: "cf_truncate_service",
    start(env) {
        // Ejecutar tras montar el webclient para evitar bloquear la carga
        queueMicrotask(() => {
            try {
                processContainer(document);
                // Observar el documento completo (ligero, solo childList + subtree)
                initObserver(document.body);
            } catch (e) {
                // console.warn("cf_truncate_service init error", e);
            }
        });
        return {};
    },
};

registry.category("services").add("cf_truncate_service", service);
