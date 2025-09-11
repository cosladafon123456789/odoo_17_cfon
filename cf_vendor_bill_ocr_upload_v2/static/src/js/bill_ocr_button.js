/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

patch(ListController.prototype, "cf_vendor_bill_ocr_upload.ListController", {
    setup() {
        this._super(...arguments);
        this.actionService = useService("action");
        this.orm = useService("orm");
    },
    get buttons() {
        const buttons = this._super(...arguments) || [];
        try {
            const model = this.props.list.model.root.env.model;
            const ctx = this.props.list.model.root.env.searchModel?.context || {};
            const moveType = ctx.default_move_type || ctx.search_default_move_type;
            const isBills = (model === "account.move") && (moveType === "in_invoice" || window.location.hash.includes("invoices"));
            if (isBills) {
                buttons.push({
                    name: "cf_subir_ocr",
                    label: _t("Subir con OCR"),
                    type: "button",
                    class: "btn btn-secondary",
                    onClick: async () => {
                        await this.actionService.doAction("cf_vendor_bill_ocr_upload.action_bill_ocr_upload_wizard");
                    },
                    sequence: 15,
                });
            }
        } catch (e) {
            // ignore
        }
        return buttons;
    },
});
