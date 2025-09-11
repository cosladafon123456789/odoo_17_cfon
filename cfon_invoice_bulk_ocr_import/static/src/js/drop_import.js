
/** CFON Drop Import for Vendor Bills (Odoo 17, OWL) */
/** Adds a small floating dropzone when viewing Vendor Bills list/kanban/form */
/** On drop, uploads files to /cfon_invoice/import and opens created bills */
odoo.define('cfon_invoice_bulk_ocr_import.drop_import', function (require) {
    "use strict";
    const { registry } = require("@web/core/registry");
    const { onMounted, onWillUnmount } = owl;
    const actionService = require("@web/core/action/action_service");
    const { useService } = require("@web/core/utils/hooks");

    const patch = require('web.utils').patch;

    // Mount a dropzone component once per action
    class DropZone extends owl.Component {
        setup() {
                this.orm = useService("orm");
            this.rpc = useService("rpc");
            this.action = useService("action");
            onMounted(this._mounted.bind(this));
            onWillUnmount(this._unmounted.bind(this));
        }
        _mounted() {
            // Create floating element
            this.el = document.createElement('div');
            this.el.className = 'cfon-dropzone';
            this.el.textContent = 'Suelta facturas aquí (OCR)';
            document.body.appendChild(this.el);

            this._onDragOver = (e) => {
                if (e.dataTransfer && e.dataTransfer.types.includes('Files')) {
                    e.preventDefault();
                    this.el.classList.add('cfon-visible');
                }
            };
            this._onDragLeave = (e) => {
                this.el.classList.remove('cfon-visible');
            };
            this._onDrop = async (e) => {
                if (!(e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length)) return;
                e.preventDefault();
                this.el.classList.add('cfon-uploading');
                try {
                    const form = new FormData();
                    for (const file of e.dataTransfer.files) {
                        form.append('files[]', file, file.name);
                    }
                    const resp = await fetch('/cfon_invoice/import', {
                        method: 'POST',
                        body: form,
                        credentials: 'same-origin',
                    });
                    if (resp.ok) {
                        const action = await resp.json();
                        this.action.doAction(action);
                    } else {
                        console.error('Upload failed');
                    }
                } catch (err) {
                    console.error(err);
                } finally {
                    this.el.classList.remove('cfon-uploading');
                    this.el.classList.remove('cfon-visible');
                }
            };

            window.addEventListener('dragover', this._onDragOver);
            window.addEventListener('dragleave', this._onDragLeave);
            window.addEventListener('drop', this._onDrop);
        }
        _unmounted() {
            if (this.el && this.el.parentNode) {
                this.el.parentNode.removeChild(this.el);
            }
            window.removeEventListener('dragover', this._onDragOver);
            window.removeEventListener('dragleave', this._onDragLeave);
            window.removeEventListener('drop', this._onDrop);
        }
    }
    DropZone.template = owl.tags.xml`<div/>`;

    // Only enable on Vendor Bills action
    const actionRegistry = registry.category("actions");
    
// Fetch config parameters once
let CFON_CFG = {vendor: true, customer: false, documents: true};
async function fetchConfig(env) {
    try {
        const params = [
            'cfon_invoice_bulk.dropzone_vendor_bills',
            'cfon_invoice_bulk.dropzone_customer_invoices',
            'cfon_invoice_bulk.dropzone_documents',
        ];
        const res = await env.services.orm.call('ir.config_parameter', 'get_param', [params[0]]);
        const res2 = await env.services.orm.call('ir.config_parameter', 'get_param', [params[1]]);
        const res3 = await env.services.orm.call('ir.config_parameter', 'get_param', [params[2]]);
        CFON_CFG.vendor = ['1','True',true,'true'].includes(res);
        CFON_CFG.customer = ['1','True',true,'true'].includes(res2);
        CFON_CFG.documents = ['1','True',true,'true'].includes(res3);
    } catch(e) { /* defaults remain */ }
}

        const original = actionRegistry.get("ir.actions.act_window");

    actionRegistry.add("ir.actions.act_window", Object.assign({}, original, {
        setup() {
                this.orm = useService("orm");
            original.setup && original.setup.apply(this, arguments);
            this._cfonZoneMounted = false;
        },
        async run(action, options) {
            const res = await original.run.call(this, action, options);
            try {
                await fetchConfig(this.env);
                    const isVendorBills = CFON_CFG.vendor && action && action.res_model === 'account.move' &&
                    ((action.context && action.context.default_move_type === 'in_invoice') ||
                     (action.domain && action.domain.toString().includes(\"'in_invoice'\")) ||
                     (action.xml_id && action.xml_id.includes('action_move_in_invoice_type')));
                const isCustomerInvoices = CFON_CFG.customer && action && action.res_model === 'account.move' && ((action.context && action.context.default_move_type === 'out_invoice') || (action.domain && action.domain.toString().includes("'out_invoice'")) || (action.xml_id && action.xml_id.includes('action_move_out_invoice_type')));
                    const isDocuments = CFON_CFG.documents && action && (action.res_model === 'documents.document' || (action.xml_id && action.xml_id.includes('documents')));
                    if ((isVendorBills || isCustomerInvoices || isDocuments) && !this._cfonZoneMounted) {
                    this._cfonZoneMounted = true;
                    const root = document.createElement('div');
                    document.body.appendChild(root);
                    const app = new owl.App(DropZone, {});
                    app.mount(root);
                }
            } catch (e) { /* ignore */ }
            return res;
        },
    }));
});
