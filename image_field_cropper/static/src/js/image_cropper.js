/** @odoo-module **/

// https://www.photoroom.com/api/docs/reference/71f4c26e59e43-remove-background-basic-plan
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { onWillStart, onMounted, useState, useRef, Component } from "@odoo/owl";
import { session } from "@web/session";

export class ImageCropperDialog extends Component {
    setup() {
        this.title = _t("Image Cropper");
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.imageRef = useRef("imageRef");

        this.state = useState({
            cropper : false,
        });

        onMounted(async () => {
            await this.render_cropper();
        });


    }

    render_cropper() {
        var self = this;
        var image = self.imageRef.el;

        var minAspectRatio = 0.5;
        var maxAspectRatio = 1.5;
        this.state.cropper = new Cropper(image, {
            scaleX: 1,
            scaleY: 1,
            ready: function () {
                var cropper = this.cropper;
                var containerData = cropper.getContainerData();
                var cropBoxData = cropper.getCropBoxData();
                var aspectRatio = cropBoxData.width / cropBoxData.height;
                var newCropBoxWidth;
        
                if (aspectRatio < minAspectRatio || aspectRatio > maxAspectRatio) {
                    newCropBoxWidth = cropBoxData.height * ((minAspectRatio + maxAspectRatio) / 2);
        
                    cropper.setCropBoxData({
                    left: (containerData.width - newCropBoxWidth) / 2,
                    width: newCropBoxWidth
                    });
                }
            },
    
            cropmove: function () {
                var cropper = this.cropper;
                var cropBoxData = cropper.getCropBoxData();
                var aspectRatio = cropBoxData.width / cropBoxData.height;
        
                if (aspectRatio < minAspectRatio) {
                    cropper.setCropBoxData({
                    width: cropBoxData.height * minAspectRatio
                    });
                } else if (aspectRatio > maxAspectRatio) {
                    cropper.setCropBoxData({
                    width: cropBoxData.height * maxAspectRatio
                    });
                }
            },
        });
    }
    onClickZoomIn(){
        this.state.cropper.zoom(0.1);
    }
    onClickZoomOut(){
        this.state.cropper.zoom(-0.1);
    }
    onClickMoveLeft(){
        this.state.cropper.move(-10,0);
    }
    onClickMoveRight(){
        this.state.cropper.move(10,0);
    }
    onClickMoveUp(){
        this.state.cropper.move(0,-10);
    }
    onClickMoveDown(){
        this.state.cropper.move(0,10);
    }
    onClickUndo(){
        this.state.cropper.rotate(-45);
    }
    onClickRedo(){
        this.state.cropper.rotate(45);
    }
    onClickFlipHorizontal(){
        this.state.cropper.scaleX(-this.state.cropper.getData().scaleX || -1);
    }
    onClickFlipVertical(){
        this.state.cropper.scaleY(-this.state.cropper.getData().scaleY || -1);
    }
    onClickCrop(){
        this.state.cropper.crop();
    }
    onClickClear(){
        this.state.cropper.clear();
    }
    onClickReload(){
        this.state.cropper.reset();
    }
    onClickConfirm(){
        var self = this;
        var croppedCanvas = this.state.cropper.getCroppedCanvas();
        croppedCanvas.toBlob(function (blob) {
            var file = new File([blob], 'cropped_image.png', {
                type: 'image/png',
                lastModified: Date.now()
            });
            self.props.uploadCropperImage(file);
            self.props.close();
        });
    }


}
ImageCropperDialog.components = { Dialog };
ImageCropperDialog.template = "image_field_cropper.ImageCropperDialog";
ImageCropperDialog.defaultProps = {
    fileurl: String,
    fileName: String,
};