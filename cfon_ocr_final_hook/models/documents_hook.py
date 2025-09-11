# -*- coding: utf-8 -*-
from odoo import api, models, _
import logging
_logger = logging.getLogger(__name__)

TARGET_MIMES = {"application/pdf", "image/jpeg", "image/png"}

class DocumentsDocumentHook(models.Model):
    _inherit = "documents.document"

    @api.model_create_multi
    def create(self, vals_list):
        docs = super().create(vals_list)
        self._cfon_try_process(docs, source="create")
        return docs

    def write(self, vals):
        res = super().write(vals)
        self._cfon_try_process(self, source="write")
        return res

    def _cfon_try_process(self, docs, source=""):
        if self.env.context.get("cfon_ocr_processing"):
            return
        folder = None
        for xmlid in [
            "cfon_ocr_final.folder_vendor_bills_ocr_pro",
            "cfon_ocr_final_hook.folder_vendor_bills_ocr_pro",
        ]:
            try:
                folder = self.env.ref(xmlid, raise_if_not_found=False)
                if folder:
                    break
            except Exception:
                folder = None
        if not folder:
            return

        to_process = docs.sudo().with_context(active_test=False).filtered(
            lambda d: d.folder_id and d.folder_id.id == folder.id
            and not d.res_model
            and d.mimetype in TARGET_MIMES
        )
        if not to_process:
            return

        engine = self.env["invoice.ocr.engine"].sudo().with_context(cfon_ocr_processing=True)
        for d in to_process:
            try:
                engine.process_document(d)
            except Exception as e:
                _logger.exception("CFON OCR: error procesando doc %s (%s): %s", d.id, source, e)
                try:
                    d.message_post(body=_("OCR: error al procesar: %s") % e)
                except Exception:
                    pass
