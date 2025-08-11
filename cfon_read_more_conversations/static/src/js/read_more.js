/** @odoo-module **/
'use strict';

/**
 * CFON Read More for Conversations (Odoo 17)
 * - Trunca el texto visible de cada mensaje a 50 caracteres.
 * - Inserta "… leer más" que, al pulsar, expande el mensaje completo.
 * - Funciona tanto en Discuss como en el Chatter, sin parchear OWL ni QWeb.
 * - Seguro: se ejecuta tras el render y usa MutationObserver para mensajes que cargan después.
 */

(function () {
    const CHAR_LIMIT = 50;

    function truncateElement(el) {
        if (!el || el.dataset.cfonProcessed === '1') return;

        // Evitar truncar elementos que no sean realmente el cuerpo de un mensaje
        // (por ejemplo, entradas de edición o compositores).
        // Si no hay texto, no hacemos nada.
        const plain = (el.textContent || '').trim();
        if (!plain) {
            el.dataset.cfonProcessed = '1';
            return;
        }

        if (plain.length <= CHAR_LIMIT) {
            el.dataset.cfonProcessed = '1';
            return;
        }

        // Guardar el HTML original para poder restaurarlo al expandir
        const fullHTML = el.innerHTML;
        el.dataset.cfonFullHtml = fullHTML;

        // Crear vista previa truncada en texto plano (para no romper marcado)
        const preview = document.createElement('span');
        preview.className = 'cfon-preview';
        preview.textContent = plain.slice(0, CHAR_LIMIT).trim() + '… ';

        const more = document.createElement('a');
        more.href = '#';
        more.className = 'cfon-read-more';
        more.textContent = 'leer más';

        more.addEventListener('click', function (ev) {
            ev.preventDefault();
            try {
                // Restaurar el HTML original
                el.innerHTML = el.dataset.cfonFullHtml || fullHTML;
                el.dataset.cfonExpanded = '1';
            } catch (e) {
                // Si algo falla, al menos mostramos el texto completo en texto plano
                el.textContent = plain;
                console.warn('[cfon_read_more] fallback plain text due to error:', e);
            }
        }, { once: true });

        // Reemplazar contenido
        el.innerHTML = '';
        el.appendChild(preview);
        el.appendChild(more);

        el.dataset.cfonProcessed = '1';
    }

    function processRoot(root) {
        try {
            const selectors = [
                // Odoo 17 Discuss / Chatter típicos
                '.o-mail-Message-body',
                '.o-mail-Message-text',
                // Variantes defensivas
                '.o_Message_content',
                '.o_Message_prettyBody'
            ];
            const elements = new Set();
            selectors.forEach(sel => {
                root.querySelectorAll(sel).forEach(el => elements.add(el));
            });
            elements.forEach(truncateElement);
        } catch (e) {
            console.warn('[cfon_read_more] processRoot error:', e);
        }
    }

    function init() {
        try {
            processRoot(document);

            // Observar nuevos mensajes que se añadan dinámicamente
            const obs = new MutationObserver((mutations) => {
                for (const m of mutations) {
                    for (const node of m.addedNodes) {
                        if (node.nodeType === 1) { // ELEMENT_NODE
                            processRoot(node);
                        }
                    }
                }
            });
            obs.observe(document.body, { childList: true, subtree: true });
        } catch (e) {
            console.warn('[cfon_read_more] init error:', e);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();