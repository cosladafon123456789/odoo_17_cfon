
/**
 * Inject "Subir facturas" button in the LIST control panel when the current model is account.move.
 * No reliance on action xmlid. Works regardless of how the user navigated.
 */
(function () {
    const BUTTON_ID = "cfon-upload-bills-btn";
    const WIZARD_XMLID = "cfon_vendor_bills_bulk_upload.action_account_vendor_bill_upload_wizard";

    function isAccountMoveList() {
        // Heuristic: there is a list renderer and the root has data-model="account.move" somewhere
        const list = document.querySelector(".o_list_renderer");
        if (!list) return false;
        // Find the closest action root which usually has data-model
        const actionRoot = list.closest("[data-model]");
        if (actionRoot && actionRoot.getAttribute("data-model") === "account.move") {
            return true;
        }
        // Fallback: check for breadcrumbs including 'Facturas' + presence of column headers typical in account.move
        const headers = Array.from(document.querySelectorAll(".o_list_table thead th")).map(th => th.textContent.trim());
        return headers.includes("Proveedor") && headers.includes("Fecha de la factura");
    }

    function addButton() {
        if (!isAccountMoveList()) return;
        const cpButtons = document.querySelector(".o_control_panel .o_cp_buttons");
        if (!cpButtons) return;
        if (document.getElementById(BUTTON_ID)) return;

        const btn = document.createElement("a");
        btn.id = BUTTON_ID;
        btn.className = "btn btn-secondary";
        btn.textContent = "Subir facturas";
        btn.setAttribute("href", "/web#action=" + WIZARD_XMLID);

        const newBtn = cpButtons.querySelector(".o_list_button_add, .o_cp_button_new, button[title='Nuevo']");
        if (newBtn && newBtn.nextSibling) {
            cpButtons.insertBefore(btn, newBtn.nextSibling);
        } else {
            cpButtons.appendChild(btn);
        }
    }

    const obs = new MutationObserver(() => addButton());
    window.addEventListener("hashchange", () => setTimeout(addButton, 50));
    window.addEventListener("load", () => setTimeout(addButton, 100));

    const root = document.body;
    if (root) obs.observe(root, { childList: true, subtree: true });
})();
