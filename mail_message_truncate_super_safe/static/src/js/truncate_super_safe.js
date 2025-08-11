\
/** @odoo-module **/
/**
 * Super seguro:
 * - Carga en web.assets_backend pero SOLO actúa tras window 'load'.
 * - Si algo falla, se silencia sin romper el cliente.
 * - Busca bloques de mensajes por múltiples señales.
 * - Encuentra el contenedor de texto más largo y lo envuelve en <details>.
 * - Umbral fijo de 50 caracteres.
 */

const THRESHOLD = 50;

// Candidatos para identificar mensajes
const MESSAGE_SELECTORS = [
    ".o-mail-Message",
    "[data-message-id]",
    "[class*='o-mail-Message']",
];

// Candidatos de cuerpo conocidos
const BODY_SELECTORS = [
    ".o-mail-Message-content",
    ".o-mail-Message-body",
    ".o-mail-Message__body",
    ".o-mail-Message__bodyWrap",
    "[data-message-body]",
    ".o-mail-Message *[data-oe-type='html']",
];

function getAllMessages(root) {
    const set = new Set();
    try {
        for (const sel of MESSAGE_SELECTORS) {
            root.querySelectorAll?.(sel)?.forEach(el => set.add(el));
        }
    } catch {}
    return Array.from(set);
}

function findBodyEl(msgEl) {
    try {
        for (const sel of BODY_SELECTORS) {
            const el = msgEl.querySelector?.(sel);
            if (el) return el;
        }
        // Fallback: escoger el descendiente con más texto
        let best = null, bestLen = 0;
        msgEl.querySelectorAll?.("p,div,section,article,pre,span").forEach(el => {
            // Evitar contenedores de controles
            if (el.closest(".cf-details-wrap")) return;
            const len = (el.textContent || "").trim().length;
            if (len > bestLen) {
                bestLen = len;
                best = el;
            }
        });
        return best || msgEl;
    } catch {
        return msgEl;
    }
}

function alreadyWrapped(bodyEl) {
    try {
        return !!bodyEl.closest(".cf-details-wrap") || !!bodyEl.querySelector(".cf-details-wrap");
    } catch {
        return true;
    }
}

function wrapBody(bodyEl) {
    try {
        if (!bodyEl || alreadyWrapped(bodyEl)) return;

        const textLen = (bodyEl.textContent || "").trim().length;
        if (textLen <= THRESHOLD) return;

        const details = document.createElement("details");
        details.className = "cf-details-wrap";
        details.open = false;

        const summary = document.createElement("summary");
        summary.className = "cf-summary";
        summary.textContent = "… Ver más";

        const content = document.createElement("div");
        content.className = "cf-content";

        // Mover nodos hijos dentro del contenido
        // (más seguro que innerHTML para no romper eventos)
        while (bodyEl.firstChild) {
            content.appendChild(bodyEl.firstChild);
        }
        details.appendChild(summary);
        details.appendChild(content);
        bodyEl.appendChild(details);

        details.addEventListener("toggle", () => {
            try {
                summary.textContent = details.open ? "Ver menos" : "… Ver más";
            } catch {}
        });
    } catch {}
}

function process(root) {
    try {
        const msgs = getAllMessages(root);
        for (const msg of msgs) {
            try {
                const body = findBodyEl(msg);
                wrapBody(body);
            } catch {}
        }
    } catch {}
}

function boot() {
    try {
        process(document);
        const obs = new MutationObserver((mut) => {
            for (const m of mut) {
                for (const n of m.addedNodes || []) {
                    if (!(n instanceof HTMLElement)) continue;
                    process(n);
                }
            }
        });
        obs.observe(document.body, { childList: true, subtree: true });
    } catch {}
}

// Ejecutar solo cuando la página ya está completamente lista
if (document.readyState === "complete") {
    setTimeout(boot, 0);
} else {
    window.addEventListener("load", () => setTimeout(boot, 0), { once: true });
}
