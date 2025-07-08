/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";

export class PrintOptionsModal extends Component {
    setup() {
        this.title = _t("What would you like to do?");
    }
    executePdfAction(option) {
        this.props.onSelectOption(option);
    }
}

PrintOptionsModal.template = "printing_options.ButtonOptions";
PrintOptionsModal.components = { Dialog };