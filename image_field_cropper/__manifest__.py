# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Cropper | Image Crop | Crop Image | Cropper Photo | Cropper Image | Cropper Editor Photo | Cropper Edit Image | Cropper Edit Photo",
    "summary": "This module allows users to select a portion of an image and crop it according to their desired dimensions.",
    "version": "17.1",
    "description": """
        This module allows users to select a portion of an image and crop it according to their desired dimensions.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/image_field_cropper.png"],
    "category": "Extra Tools",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "/image_field_cropper/static/src/lib/*.*",
            "/image_field_cropper/static/src/js/*.*",
        ],
    },
    "installable": True,
    "application": True,
    "price"                :  40,
    "currency"             :  "EUR",
}
