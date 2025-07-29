/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ImageField } from '@web/views/fields/image/image_field';
import { patch } from "@web/core/utils/patch";
import { isBinarySize } from "@web/core/utils/binary";
import { url } from "@web/core/utils/urls";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { ImageCropperDialog } from "./image_cropper"

import { fileTypeMagicWordMap, imageCacheKey } from "@web/views/fields/image/image_field";
const { DateTime } = luxon;

patch(ImageField.prototype, {
    setup(...args) {
        super.setup(...args);
        this.dialog = useService("dialog");
        this.notification = useService("notification");
    },

    onFilePhotoroomEdit(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        
        var self = this;
        var fileurl = "";

        if (this.state.isValid && this.props.record.data[this.props.name]) {
            if (isBinarySize(this.props.record.data[this.props.name])) {
                fileurl =  url("/web/image", {
                    model: this.props.record.resModel,
                    id: this.props.record.resId,
                    field: this.props.name,
                    unique: imageCacheKey(this.rawCacheKey),
                });
            }else {
                // Use magic-word technique for detecting image type
                const magic = fileTypeMagicWordMap[this.props.record.data[this.props.name][0]] || "png";
                fileurl = `data:image/${magic};base64,${this.props.record.data[this.props.name]}`;
            }
        }

        if (fileurl){
            const magic = fileTypeMagicWordMap[this.props.record.data[this.props.name][0]] || "png";
            self.dialog.add(ImageCropperDialog, {
                fileName : self.props.name + '.' + magic,
                fileurl: fileurl,
                uploadCropperImage: (file) => this.uploadCropperImage(file),
            });
        }
    },
    uploadCropperImage(file){
        var self = this;
        if (!file) {
            return Promise.reject();
        }
        return new Promise(function (resolve, reject) {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = async function () {
                resolve(reader.result);
                var data = reader.result;
                data = data.split(',')[1];
                self.props.record.update({ [self.props.name]: data || false });
                self.state.isValid = true;  
            }
            reader.onerror = function (error) {
                reject(error)
            }
        });
    }
});
