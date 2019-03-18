<template>
    <div>
        <form-accordion :visible="is_visible">
            <template slot="header">
                <span>{{ gettext('Barcode') }} {{ barcodeKind }}</span>
            </template>
            <template slot="body">

                <div class="row mb-4">
                    <div class="col-12">
                        <!-- barcode kind description -->
                        <div class="card">
                            <div class="card-body">
                                <div v-if="packageLevel === 30" class="text-center mb-2">
                                    <!-- Palette -->
                                    <a href="https://www.gs1ie.org/tools-services/logistics-label-tool/">
                                        <h3>{{ gettext('Logistics Label Tool') }}</h3>
                                    </a>
                                </div>

                                <div v-if="barcodeKind === 'UPCA'">
                                    <p>todo: description for UPCA</p>
                                </div>

                                <div v-else-if="barcodeKind === 'EAN13'">
                                    {{
                                        gettext(
                                            'The family of EAN/UPC barcodes are used to represent GTINs on trade items so they can be scanned at' +
                                            'Point-of-Sale and distribution centers. They should only be printed on outer-cases if they are printed' +
                                            'at 200% their size and the case will be scanned at the point of sale. A case of wine is an example of such a product')
                                    }}
                                </div>

                                <div v-else-if="barcodeKind === 'ITF14'">
                                    {{
                                        gettext(
                                            'The ITF 14 symbol is used for trade items not passing the point of sale and is ideal for use where the' +
                                            'symbol is to be pre-printed onto corrugated fibreboard/Kraftboard or onto labels attached outer cases.')
                                    }}

                                </div>

                                <div v-else class="text-center">
                                    {{ gettext('Barcodes for this package level are not supported') }}
                                </div>

                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="barcodeKind" class="row mb-4 barcode-details">
                    <div class="col-6 text-center preview-container">
                        <img v-if="barcodeImage" :src="barcodeImage" class="barcode-preview">
                        <spinner-indicator :loading="!barcodeImage" class="image-spinner">
                        </spinner-indicator>
                    </div>

                    <!-- barcode options start -->
                    <div v-if="barcodeSectionsDisplayed" class="col-6 barcode-options">
                        <form-accordion :name="'raster_simple'"
                                        v-if="barcodeSectionsOptions.raster_simple.enabled"
                                        :visible="barcodeSectionsOptions.raster_simple.visible"
                                        @on_visibility_change="onSectionVisibilityChange">
                            <template slot="header">
                                <span>{{ gettext('Download raster image') }}</span>
                            </template>
                            <template slot="body">
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.size.errors"
                                            v-model="barcodeParameters.size.value"
                                            :choices="_.map(barcodeParameters.size.enum, item => [item[0], (item[1] * 100).toFixed(0) + '%'])"
                                            :label="barcodeParameters.size.title"
                                            :name="'size'"
                                            :required="barcodeParameters.size.required"
                                            :valuetype="barcodeParameters.size.type"
                                            :description="barcodeParameters.size.description"
                                            :readonly="barcodeParameters.size.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        <ul>
                                            <li>{{ gettext('Image type') }}: <strong>{{ barcodeParameters.image_type.value }}</strong></li>
                                            <li>{{ gettext('Resolution') }}: <strong>{{ barcodeParameters.resolution.value }}</strong></li>
                                            <li>{{ gettext('Magnification') }}: <strong>{{ (barcodeParameters.size.value * 100).toFixed(0) }}%</strong></li>
                                        </ul>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12 my-2 text-center">
                                        <b-button variant="primary" @click.prevent="generateAndDownloadBarcode('raster')">
                                            {{ gettext('Download raster image') }}
                                        </b-button>
                                    </div>
                                </div>
                            </template>
                        </form-accordion>

                        <!-- barcode options: raster image download -->
                        <form-accordion :name="'raster'"
                                        v-if="barcodeSectionsOptions.raster.enabled"
                                        :visible="barcodeSectionsOptions.raster.visible"
                                        @on_visibility_change="onSectionVisibilityChange">
                            <template slot="header">
                                <span>{{ gettext('Download raster image') }}</span>
                            </template>
                            <template slot="body">
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.image_type.errors"
                                            v-model="barcodeParameters.image_type.value"
                                            :choices="barcodeParameters.image_type.enum"
                                            :label="barcodeParameters.image_type.title"
                                            :name="'image_type'"
                                            :required="barcodeParameters.image_type.required"
                                            :valuetype="barcodeParameters.image_type.type"
                                            :description="barcodeParameters.image_type.description"
                                            :readonly="barcodeParameters.image_type.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.resolution.errors"
                                            v-model="barcodeParameters.resolution.value"
                                            :choices="barcodeParameters.resolution.enum"
                                            :label="barcodeParameters.resolution.title"
                                            :name="'resolution'"
                                            :required="barcodeParameters.resolution.required"
                                            :valuetype="barcodeParameters.resolution.type"
                                            :description="barcodeParameters.resolution.description"
                                            :readonly="barcodeParameters.resolution.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12 mt-3 mb-2 text-center">
                                        <b-button variant="primary" @click.prevent="generateAndDownloadBarcode('raster')">
                                            {{ gettext('Download raster image') }}
                                        </b-button>
                                    </div>
                                </div>
                            </template>
                        </form-accordion>

                        <!-- barcode options: postscript download -->
                        <form-accordion :name="'ps'"
                                        v-if="barcodeSectionsOptions.ps.enabled"
                                        :visible="barcodeSectionsOptions.ps.visible"
                                        @on_visibility_change="onSectionVisibilityChange">
                            <template slot="header">
                                <span>{{ gettext('Download postscript (eps) image') }}</span>
                            </template>
                            <template slot="body">
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.ps_type.errors"
                                            v-model="barcodeParameters.ps_type.value"
                                            :choices="barcodeParameters.ps_type.enum"
                                            :label="barcodeParameters.ps_type.title"
                                            :name="'ps_type'"
                                            :required="barcodeParameters.ps_type.required"
                                            :valuetype="barcodeParameters.ps_type.type"
                                            :description="barcodeParameters.ps_type.description"
                                            :readonly="barcodeParameters.ps_type.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12 mt-3 mb-2 text-center">
                                        <b-button variant="primary" @click.prevent="generateAndDownloadBarcode('ps')">
                                            {{ gettext('Download postscript(eps) image') }}
                                        </b-button>
                                    </div>
                                </div>
                            </template>
                        </form-accordion>

                        <!-- barcode options: pdf download -->
                        <form-accordion :name="'label'"
                                        v-if="barcodeSectionsOptions.label.enabled"
                                        :visible="barcodeSectionsOptions.label.visible"
                                        @on_visibility_change="onSectionVisibilityChange">
                            <template slot="header">
                                <span>{{ gettext('Download PDF labels') }}</span>
                            </template>
                            <template slot="body">
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.label_type.errors"
                                            v-model="barcodeParameters.label_type.value"
                                            :choices="barcodeParameters.label_type.enum"
                                            :label="barcodeParameters.label_type.title"
                                            :name="'label_type'"
                                            :required="barcodeParameters.label_type.required"
                                            :valuetype="barcodeParameters.label_type.type"
                                            :description="barcodeParameters.label_type.description"
                                            :readonly="barcodeParameters.label_type.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12 mt-3 mb-2 text-center">
                                        <b-button variant="primary" @click.prevent="generateAndDownloadBarcode('label')">
                                            {{ gettext('Download PDF labels') }}
                                        </b-button>
                                    </div>
                                </div>

                                <!-- fixme: preview is temporary disabled: missing label previews!  -->
                                <div class="row" v-if="false && getLabelPreview()">
                                    <div class="col-12">
                                        <h5>{{ gettext('Sample') }}</h5>
                                        <img :src="getLabelPreview()">
                                    </div>
                                </div>
                                <div class="row mt-2">
                                    <div class="col-12" v-html="getLabelDescription()"></div>
                                </div>
                            </template>
                        </form-accordion>

                        <!-- barcode options: image options -->
                        <form-accordion :name="'options'"
                                        v-if="barcodeSectionsOptions.options.enabled"
                                        :visible="barcodeSectionsOptions.options.visible"
                                        @on_visibility_change="onSectionVisibilityChange">
                            <template slot="header">
                                <span>{{ gettext('Image Options') }}</span>
                            </template>
                            <template slot="body">
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.size.errors"
                                            v-model="barcodeParameters.size.value"
                                            :choices="barcodeParameters.size.enum"
                                            :label="barcodeParameters.size.title"
                                            :name="'size'"
                                            :required="barcodeParameters.size.required"
                                            :valuetype="barcodeParameters.size.type"
                                            :description="barcodeParameters.size.description"
                                            :readonly="barcodeParameters.size.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.bwr.errors"
                                            v-model="barcodeParameters.bwr.value"
                                            :choices="barcodeParameters.bwr.enum"
                                            :label="barcodeParameters.bwr.title"
                                            :name="'bwr'"
                                            :required="barcodeParameters.bwr.required"
                                            :valuetype="barcodeParameters.bwr.type"
                                            :description="barcodeParameters.bwr.description"
                                            :readonly="barcodeParameters.bwr.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.rqz.errors"
                                            v-model="barcodeParameters.rqz.value"
                                            :choices="barcodeParameters.rqz.enum"
                                            :label="barcodeParameters.rqz.title"
                                            :name="'rqz'"
                                            :required="barcodeParameters.rqz.required"
                                            :valuetype="barcodeParameters.rqz.type"
                                            :description="barcodeParameters.rqz.description"
                                            :readonly="barcodeParameters.rqz.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.marks.errors"
                                            v-model="barcodeParameters.marks.value"
                                            :choices="barcodeParameters.marks.enum"
                                            :label="barcodeParameters.marks.title"
                                            :name="'marks'"
                                            :required="barcodeParameters.marks.required"
                                            :valuetype="barcodeParameters.marks.type"
                                            :description="barcodeParameters.marks.description"
                                            :readonly="barcodeParameters.marks.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-12">
                                        <field-with-errors
                                            :errors="barcodeParameters.debug.errors"
                                            v-model="barcodeParameters.debug.value"
                                            :choices="barcodeParameters.debug.enum"
                                            :label="barcodeParameters.debug.title"
                                            :name="'debug'"
                                            :required="barcodeParameters.debug.required"
                                            :valuetype="barcodeParameters.debug.type"
                                            :description="barcodeParameters.debug.description"
                                            :readonly="barcodeParameters.debug.readonly">
                                        </field-with-errors>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-12 mt-3 mb-2 text-center">
                                        <b-button variant="primary" @click.prevent="generateAndPreviewBarcode()">
                                            {{ gettext('Update barcode preview') }}
                                        </b-button>
                                    </div>
                                </div>
                            </template>
                        </form-accordion>
                    </div>
                    <!-- barcode options end -->

                    <div v-else class="col-6">
                        <!-- welcome message to barcode creation -->
                        <p>
                            <b>{{ gettext('Create and download a high resolution image of this barcode.') }}</b>
                            {{
                                gettext(
                                    'Available formats are JPG, PNG and GIF raster images up to 2400dpi resolution,' +
                                    'and postscript images which scale to your desired size.')
                            }}

                        </p>
                        <p>
                            {{ gettext('To create your barcode image you need to have at least 1 credit available in your balance.') }}
                        </p>

                        <a @click.prevent="checkBarcodeAgreement" href="#" class="btn btn-primary">{{ gettext('Create EAN13 barcode') }}</a>
                    </div>
                </div>


            </template>
        </form-accordion>

        <base-agreement-modal
            ref="barcodeAgreementModal"
            :title_text="gettext('Agreement required')"
            :text="_.get(user, 'barcode_disclaimer', gettext('Please contact us for the agreement text'))"
            @ok="showBarcodeOptions()">
        </base-agreement-modal>

    </div>
</template>


<script>
    import FormAccordion from './FormAccordion';
    import BaseAgreementModal from './modals/BaseAgreementModal';
    import FieldWithErrors from '../../common/components/FieldWithErrors';
    import SpinnerIndicator from "../../common/components/SpinnerIndicator";
    import _ from 'lodash';

    export default {
        components: {
            FormAccordion,
            BaseAgreementModal,
            SpinnerIndicator,
            FieldWithErrors,
        },
        props: {
            user: {
                required: true,
            },
            formData: {
                required: true,
            },
        },
        data() {
            return {
                is_visible: true,  // top form accordion
                isBarcodeAgreementModalOpen: false,
                barcodeImage: undefined, // barcode preview or barcode
                barcodeSectionsDisplayed: false,
                barcodeSectionsOptions: {
                    'raster_simple': {
                        'visible': false,
                        'enabled': false,
                    },
                    'raster': {
                        'visible': false,
                        'enabled': true,
                    },
                    'ps': {
                        'visible': false,
                        'enabled': true,
                    },
                    'label': {
                        'visible': false,
                        'enabled': true,
                    },
                    'options': {
                        'visible': false,
                        'enabled': true,
                    },
                },
                simplifiedBarcodeGeneration: this.user.simplified_barcode_generation,
                barcodeSimplifiedDefaults: {
                    "image_type": "jpg",
                    "resolution": "2400 dpi",
                    'barcode_sections': {
                        // this sections will be configured for the simplified version
                        // all other sections will be disabled
                        'raster_simple': {
                            'visible': true,
                            'enabled': true,
                        },
                        'label': {
                            'visible': false,
                            'enabled': true,
                        },
                    },
                },
                barcodeParameters: {
                    "image_type": {
                        "title": gettext('File type'),
                        "description": gettext('Image file type'),
                        "type": "string",
                        "enum": [
                            ['png', 'PNG'],
                            ['gif', 'GIF'],
                            ['jpg', 'JPG'],
                        ],
                        "dataById": {},
                        "errors": [],
                        'value': 'gif',
                        "required": true,
                        "readonly": false
                    },
                    "resolution": {
                        "title": gettext('Printer resolution'),
                        "description": gettext('Printer resolution'),
                        "type": "string",
                        "enum": [
                            ['300 dpi', '300 DPI'],
                            ['600 dpi', '600 DPI'],
                            ['1200 dpi', '1200 DPI'],
                            ['2400 dpi', '2400 DPI'],
                        ],
                        "dataById": {},
                        "errors": [],
                        'value': '300 dpi',
                        "required": true,
                        "readonly": false
                    },
                    "ps_type": {
                        "title": gettext('Postscript type'),
                        "description": gettext('Postscript (eps) image type'),
                        "type": "string",
                        "enum": [
                            ['win', 'Windows'],
                            ['mac', 'Mac'],
                        ],
                        "dataById": {},
                        "errors": [],
                        'value': 'win',
                        "required": true,
                        "readonly": false
                    },
                    "label_type": {
                        "title": gettext('Label type'),
                        "description": gettext('PDF label type'),
                        "type": "string",
                        "enum": [],
                        "dataById": {},
                        "errors": [],
                        'value': 'win',
                        "required": true,
                        "readonly": false
                    },
                    "size": {
                        "title": gettext('Magnification'),
                        "description": gettext('Magnification'),
                        "type": "string",
                        "enum": this.retrieveSizeOptions(0.8, 2.0, 0.05),
                        "dataById": {},
                        "errors": [],
                        "value": "0.8",
                        "required": true,
                        "readonly": false
                    },
                    "bwr": {
                        "title": gettext('BWR'),
                        "description": gettext(
                            'BWR stands for bar-width reduction ' +
                            'and compensates for the ink-spread during printing.'
                        ),
                        "type": "string",
                        "enum": this.retrieveBWROptions(0.0000, 0.0050, 0.0005),
                        "dataById": {},
                        "errors": [],
                        "value": "0.0000",
                        "required": true,
                        "readonly": false
                    },
                    "rqz": {
                        "title": gettext('Right quiet zone indicator'),
                        "description": gettext('Right quiet zone indicator'),
                        "type": "boolean",
                        "errors": [],
                        "value": true,
                        "required": false,
                        "readonly": false
                    },
                    "marks": {
                        "title": gettext('Printing Marks'),
                        "description": gettext('Printing Marks'),
                        "type": "boolean",
                        "errors": [],
                        "value": false,
                        "required": false,
                        "readonly": false
                    },
                    "debug": {
                        "title": gettext('Calibration (Debug)'),
                        "description": gettext('Calibration (Debug)'),
                        "type": "boolean",
                        "errors": [],
                        "value": false,
                        "required": false,
                        "readonly": false
                    },
                },
            };
        },
        methods: {
            gettext(text) {
                return gettext(text);
            },
            checkBarcodeAgreement() {
                if(this.agreedBarcodeDisclaimer) {
                    // show barcode dialog
                    this.showBarcodeOptions()
                } else {
                    this.$refs.barcodeAgreementModal.open();
                }
            },
            applySimplifiedDefaults() {
                if(this.simplifiedBarcodeGeneration) {
                    // default parameters for images
                    _.each(this.barcodeSimplifiedDefaults, (value, key) => {
                        _.set(this.barcodeParameters, `${key}.value`, value);
                    });

                    // display and expand/collapse required sections
                    let simplified_sections = this.barcodeSimplifiedDefaults.barcode_sections;
                    let current_sections = this.barcodeSectionsOptions;

                    _.each(current_sections, (section, section_name) => {
                        if(_.has(simplified_sections, section_name)) {
                            current_sections[section_name] = simplified_sections[section_name];
                        } else {
                            current_sections[section_name] = {'enabled': false, 'visible': false};
                        }
                    });
                }
                // if it will be required to switch on/off simplified mode
                // it's required to implement switch to "full mode" here
            },
            showBarcodeOptions() {
                if(this.agreedBarcodeDisclaimer) {
                    this.generateAndPreviewBarcode();
                    this.barcodeSectionsDisplayed = true;
                    return;
                }

                let api_url = `/api/v1/users/${this.user.id}/update`;
                let patch_data = {'agreed_barcode_disclaimer': true};

                this.$http.patch(api_url, patch_data).then(
                    response => {
                        // if user agreed
                        if(response.body.agreed_barcode_disclaimer) {
                            this.generateAndPreviewBarcode();
                            this.barcodeSectionsDisplayed = true;
                        } else {
                            console.log('There is no agreement for barcodes generating');
                        }
                    },
                    response => {
                        console.log('API Error:', response.body);
                    },
                );
            },
            onSectionVisibilityChange({name, val}) {
                this.barcodeSectionsOptions[name].visible = val;

                if(val) {
                    // collapse all other "barcodeSectionsOptions" named tabs
                    _.forEach(this.barcodeSectionsOptions, (section, key) => {
                        if(key !== name) {
                            this.barcodeSectionsOptions[key].visible = false;
                        }
                    });
                }
            },
            retrieveImage(watermark_preview, barcode_parameters) {
                let send_data = barcode_parameters ? barcode_parameters : {};

                let type = watermark_preview ? 'preview' : 'generate';
                let api_url = `/api/v1/barcodes/${this.gtin}/${type}/`;
                let update_preview = false;

                if(!send_data.download_type) {
                    update_preview = true;
                    this.barcodeImage = undefined;
                }

                return this.$http.get(api_url, {'params': send_data}).then(
                    response => {
                        let barcode = response.body.barcode;
                        if(update_preview) {
                            // when we downloading a file don't show a preview
                            this.barcodeImage = barcode;
                        }
                        return barcode;
                    },
                    response => {
                        console.log('API Error:', response.body);
                        return undefined;  // barcodeImage is already set to undefined here
                    },
                )
            },
            generateAndDownloadBarcode(download_type) {
                let download_parameters = {
                    'download_type': download_type,
                    'size': _.get(this, 'barcodeParameters.size.value', ''),
                    'bwr': _.get(this, 'barcodeParameters.bwr.value', ''),
                    'resolution': _.get(this, 'barcodeParameters.resolution.value', ''),
                    'file_type': _.get(this, 'barcodeParameters.image_type.value', ''),
                    'ps_type': _.get(this, 'barcodeParameters.ps_type.value', ''),
                    'label_type': _.get(this, 'barcodeParameters.label_type.value', ''),
                    'rqz': _.get(this, 'barcodeParameters.rqz.value', ''),
                    'marks': _.get(this, 'barcodeParameters.marks.value', ''),
                    'debug': _.get(this, 'barcodeParameters.debug.value', ''),
                };

                this.retrieveImage(false, download_parameters).then(
                    file_path => {this.userDownloadFileByPath(file_path)}
                );
            },
            generateAndPreviewBarcode() {
                let preview_parameters = {
                    'size': _.get(this, 'barcodeParameters.size.value', ''),
                    'bwr': _.get(this, 'barcodeParameters.bwr.value', ''),
                    'rqz': _.get(this, 'barcodeParameters.rqz.value', ''),
                    'marks': _.get(this, 'barcodeParameters.marks.value', ''),
                    'debug': _.get(this, 'barcodeParameters.debug.value', ''),
                };

                this.retrieveImage(false, preview_parameters)
            },
            userDownloadFileByPath(file_path) {
                // initiate a file downloading,
                // with behaviour like a user clicks on a link
                if(!file_path) {
                    console.log('can\'t download a file, empty path');
                    return;
                }

                let element = document.createElement('a');
                let file_name = file_path.split(/[\\/]/).slice(-1)[0];
                element.setAttribute('href', file_path);
                element.setAttribute('download', file_name);
                element.style.display = 'none';
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
            },
            retrievePDFLabels() {
                return this.$http.get(`/api/v1/barcodes/labels/`).then(
                    response => {
                        let label_types = response.body;
                        this.barcodeParameters.label_type.enum = [];
                        this.barcodeParameters.label_type.dataById = {};

                        _.forEach(label_types, (label_type) => {
                            this.barcodeParameters.label_type.enum.push(
                                [label_type.code, label_type.short_desc]
                            );
                            this.barcodeParameters.label_type.dataById[label_type.code] = label_type;
                        });

                        this.barcodeParameters.label_type.value = _.get(
                            label_types, '[0].code', undefined
                        );
                        return label_types;
                    },
                    response => {
                        console.log('API Error:', response);
                        this.barcodeParameters.label_type.enum = [];
                        this.barcodeParameters.label_type.dataById = {};
                        this.barcodeParameters.label_type.value = undefined;
                        return undefined;
                    },
                )
            },
            getLabelDescription() {
                return _.get(
                    this.barcodeParameters,
                    `label_type.dataById.${this.barcodeParameters.label_type.value}.description`,
                    ''
                )
            },
            getLabelPreview() {
                return _.get(
                    this.barcodeParameters,
                    `label_type.dataById.${this.barcodeParameters.label_type.value}.src`,
                    ''
                )
            },
            retrieveSizeOptions(start, end, step) {
                let options = [];
                let width = String(step).length - 2;

                for(let i = start; i.toFixed(width) <= end; i += step) {
                    let current_value = i.toFixed(width);
                    options.push([current_value, current_value])
                }
                return options;
            },
            retrieveBWROptions(start, end, step) {
                let options = this.retrieveSizeOptions(start, end, step);
                let predefined_values = {
                    '0.0015':  gettext('0.0015 (printer resolution 600 dpi)'),
                    '0.0035': gettext('0.0035 (printer resolution 300 dpi)'),
                };
                _.forEach(options, (value, key) => {
                    options[key][1] = _.get(
                        predefined_values, options[key][1], options[key][1]
                    );
                });
                return options;
            },
        },
        computed: {
            _() {
                // lodash for templates
                return _;
            },
            packageLevel() {
                return _.get(this, 'formData.package_level.value', undefined);
            },
            gtin() {
                return _.get(this, 'formData.gtin.value', undefined);
            },
            gtin13() {
                if(this.gtin) {
                    return this.gtin.substring(1, 14);
                } else {
                    return undefined;
                }
            },
            agreedBarcodeDisclaimer() {
                return _.get(this, 'user.agreed_barcode_disclaimer', null);
            },
            barcodeKind() {
                if (this.packageLevel >= 40 && this.packageLevel <= 70) {
                    if (this.packageLevel === 70) {
                        if (_.startsWith(this.gtin13, '0')) {
                            return 'UPCA';
                        } else {
                            return 'EAN13';
                        }
                    } else {
                        return 'ITF14';
                    }
                }
                return undefined;
            },
        },
        watch: {
            simplifiedBarcodeGeneration(value) {
                // not required right now, but will be useful
                // if simple/full interface switcher will be implemented
                this.applySimplifiedDefaults();
            },
        },
        mounted() {
            if(this.barcodeKind) {
                this.retrieveImage(true, null);  // preview with watermark
            }
            this.retrievePDFLabels();
            this.applySimplifiedDefaults();  // if required
        },
    }
</script>

<style>
    .barcode-options .collapse-activator {
        font-size: 1rem;
        /* prevent captions text selection */
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
</style>

<style scoped>
    .preview-container {
        position: relative;
        height: 250px;
    }
    .barcode-preview {
        position:absolute;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        margin: auto;
        min-width: 230px;
        max-width: 300px;
    }
    .barcode-details {
        min-height: 230px;
    }
    .image-spinner {
        width: 100%;
        height: 100%;
        margin: 0;
    }
</style>
