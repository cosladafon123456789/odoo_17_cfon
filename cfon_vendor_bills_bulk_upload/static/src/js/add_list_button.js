
/**
 * Adds a visible "Subir facturas" button in the vendor bills LIST control panel.
 * It links to the wizard action via hash URL so it opens in a modal (target=new).
 * Tested with Odoo 17 Enterprise/Community.
 */
(function () {
    const BUTTON_ID = "cfon-upload-bills-btn";
    const ACTION_XMLID = "account.action_move_in_invoice_type"; // Vendor Bills list action
    const WIZARD_XMLID = "cfon_vendor_bills_bulk_upload.action_account_vendor_bill_upload_wizard";

    function isOnVendorBillsAction() {
        const hash = window.location.hash || "";
        // Works if action is referenced by xmlid or numeric id after a redirect
        return hash.includes("action=" + ACTION_XMLID) || hash.includes("action=account.action_move_in_invoice_type");
    }

    function addButton() {
        if (!isOnVendorBillsAction()) {
            return;
        }
        const cpButtons = document.querySelector(".o_control_panel .o_cp_buttons");
        if (!cpButtons) return;
        if (document.getElementById(BUTTON_ID)) return;

        const btn = document.createElement("a");
        btn.id = BUTTON_ID;
        btn.className = "btn btn-secondary";
        btn.textContent = "Subir facturas";
        // Open the wizard by xmlid via hash (Odoo resolves it); target=new makes it a modal
        btn.setAttribute("href", "/web#action=" + WIZARD_XMLID);
        // Insert after "Nuevo" button if exists
        const newBtn = cpButtons.querySelector(".o_list_button_add, .o_cp_button_new, button[title='Nuevo']");
        if (newBtn && newBtn.nextSibling) {
            cpButtons.insertBefore(btn, newBtn.nextSibling);
        } else {
            cpButtons.appendChild(btn);
        }
    }

    // Initial try and on URL/hash changes
    const obs = new MutationObserver(() => addButton());
    window.addEventListener("hashchange", () => setTimeout(addButton, 50));
    window.addEventListener("load", () => setTimeout(addButton, 100));

    const root = document.body;
    if (root) {
        obs.observe(root, { childList: true, subtree: true });
    }
})();
