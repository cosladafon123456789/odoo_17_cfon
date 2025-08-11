\
/** @odoo-module **/
/**
 * Trunca mensajes largos en el hilo de 'Conversaciones' (Discuss) y en el chatter.
 * - Si el texto plano del cuerpo supera 500 caracteres, se colapsa visualmente.
 * - Muestra un botón "… Ver más" para expandir y "Ver menos" para volver a colapsar.
 * - No modifica el HTML original del mensaje: solo aplica clases CSS y toggles.
 * - Usa MutationObserver para actuar cuando llegan nuevos mensajes.
 */

const THRESHOLD = 500;

// Selectores probados en Odoo 17 (pueden variar con themes/ajustes):
// - Contenedor de un mensaje en Discuss/Chatter: .o-mail-Message
// - Cuerpo del mensaje (contenido): .o-mail-Message-content, .o-mail-Message-body, o [data-message-body]
const MESSAGE_SELECTOR = ".o-mail-Thread, .o-mail-FormChatter, .o_Chatter"; // contenedores donde observar
const BODY_CANDIDATES = [
    ".o-mail-Message-content",
    ".o-mail-Message-body",
    ".o-mail-Message__body",
    "[data-message-body]",
    ".o-mail-Message *[data-oe-type='html']",
];

function findBodyEl(msgEl) {
    for (const sel of BODY_CANDIDATES) {
        const el = msgEl.querySelector(sel);
        if (el) return el;
    }
    // Fallback: todo el contenido del mensaje
    return msgEl;
}

function ensureControls(msgEl, bodyEl) {
    if (msgEl.classList.contains("cf-truncated-ready")) return;
    const textLen = (bodyEl.textContent || "").trim().length;
    if (textLen <= THRESHOLD) {
        msgEl.classList.add("cf-truncated-skip");
        return;
    }

    // Crear contenedor de controles
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

    controls.appendChild(btn);

    // Insertar controles al pie del cuerpo (si no existe ya)
    if (!bodyEl.parentElement.querySelector(".cf-truncate-controls")) {
        bodyEl.parentElement.appendChild(controls);
    }

    // Marcar como preparado y colapsado por defecto
    msgEl.classList.add("cf-truncated-ready");
    msgEl.classList.remove("cf-expanded");
}

function processExisting() {
    // Buscar mensajes dentro de los contenedores relevantes
    document.querySelectorAll(".o-mail-Message").forEach((msg) => {
        try {
            const body = findBodyEl(msg);
            if (body) ensureControls(msg, body);
        } catch (e) {
            // Silenciar errores individuales para no romper el backend
            // console.warn("truncate_messages error:", e);
        }
    });
}

// Observa dinámicamente los hilos
function initObserver(root) {
    const obs = new MutationObserver((mutations) => {
        for (const m of mutations) {
            for (const node of m.addedNodes || []) {
                if (!(node instanceof HTMLElement)) continue;
                if (node.matches(".o-mail-Message")) {
                    const body = findBodyEl(node);
                    if (body) ensureControls(node, body);
                } else {
                    node.querySelectorAll?.(".o-mail-Message").forEach((msg) => {
                        const body = findBodyEl(msg);
                        if (body) ensureControls(msg, body);
                    });
                }
            }
        }
    });
    obs.observe(root, { childList: true, subtree: true });
}

function boot() {
    // Procesar lo que ya esté en pantalla
    processExisting();
    // Observar en cada contenedor relevante
    document.querySelectorAll(MESSAGE_SELECTOR).forEach((root) => {
        initObserver(root);
    });

    // Como fallback, observar el body entero (por si cambia de vista)
    initObserver(document.body);
}

// Retrasar hasta tener el backend listo
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
} else {
    setTimeout(boot, 0);
}
