<template>
    <div>


        <div v-if="loaded">

            <b-alert show variant="danger" v-for="error in nonFieldErrors">{{ error }}</b-alert>

            <product-translation v-if="formData.language.enum.length>0"
                                 :form-data="formData"
                                 :languages="formData.language.enum"
                                 :current-language="language"
                                 @change="changeLanguages($event)"
                                 @set-active="setActiveLanguage($event)"
                                 @click-field="clickField($event)"
            />
            <form
                    method="post" enctype="multipart/form-data" id="detailsform" class="ProductFullEdit"
                    :class="{'ProductFullEdit--optionalFieldsError': $refs.basicFormOptions ?
                             $refs.basicFormOptions.optionalFieldsError:false}"
                    ref="ProductFullEdit">

                <input type="hidden" name="gtin" :value="formData.gtin.value" id="gtin" v-if="formData.gtin"
                       readonly="readonly"/>
                <input
                        type="hidden" name="bar_placement" :value="formData.bar_placement.value" id="bar_placement"
                        v-if="formData.bar_placement"/>
                <input
                        type="hidden" name="package_level" :value="formData.package_level.value" id="package_level"
                        v-if="formData.package_level"/>

                <b-tabs :value="tabIdx">
                    <b-tab :title="gettext('Basic')" @click="locationHash='#/basic'"
                           :active="locationHash === '#/basic'">

                        <form-accordion :visible="true" >
                            <template slot="header">{{ gettext('Product Identification') }}</template>
                            <template slot="body">
                                <div class="card">
                                    <div class="card-body">
                                        <p class="card-text">{{ gettext('When giving the barcode number for a product to your printer/graphic designer/packaging designer for the creation of a barcode symbol, please ignore the preceding 0 attached to the barcode number below if the package level is a base unit and inner case. Keep the 0 if the package level is an outer case or pallet.') }}</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-12'>
                                        <fieldset class='fieldset' style="border-color: #dd0000">
                                            <legend>{{ gettext('GTIN') }}</legend>
                                            <span v-if="formData.package_level.value != 70 || enableLeading">
                                        <input
                                                class="form-control"
                                                :readonly="enableLeading"
                                                size="1"
                                                maxlength="1"
                                                id="gtin0"
                                                name="gtin0"
                                                type="number"
                                                min="0"
                                                max="9"
                                                v-model="gtin0"
                                                style="display:inline;width:15%;text-align:right;font-weight:bold;font-size:1.5em;width:5ch;height:3em"
                                                @click="calculateCheckDigit()"
                                                @keyup="calculateCheckDigit()"/>

                                            <span v-if="formData.package_level.value != 70 ">
                                                 <input
                                                         class="form-control leading-control"
                                                         :class="{'leading-control--readonly':leadingReadonly}"
                                                         :readonly="leadingReadonly"
                                                         size="1"
                                                         maxlength="1"
                                                         id="gtin0"
                                                         name="gtin0"
                                                         :type="leadingReadonly?'text':'number'"
                                                         min="0"
                                                         max="9"
                                                         v-model="gtin0"
                                                         @click="calculateCheckDigit()"
                                                         @keyup="calculateCheckDigit()"/>
                                            </span>
                                            <span v-else-if="mo_info.show_leading_digit">
                                                  <span class="gtin13-class">0</span>
                                            </span>
                                            <span v-else></span>


                                            <div id="gtin13" class="gtin13-class">
                                                <template v-if="kind === 'EAN13'">
                                                    <b>
                                                        {{ gtin13|substring(0, prefix.length)}}
                                                    </b>
                                                </template>
                                                <template v-else-if="kind === 'UPCA'">
                                                    <b>
                                                        {{ gtin13|substring(1, prefix.length)}}
                                                    </b>
                                                </template>
                                                <span style="color:#F26334">
                                            {{ gtin13|substring(prefix.length, gtin13.length - 1)}}
                                        </span>
                                                <span id="cd">{{ cd }}</span>
                                            </div>
                                        </fieldset>
                                        <br/>
                                    </div>
                                    <div class="col-9">
                                        <field-with-errors
                                                :errors="formData.package_type.errors"
                                                v-model="formData.package_type.value"
                                                :name="'package_type'"
                                                :label="formData.package_type.title"
                                                :valuetype="formData.package_type.type"
                                                :choices="formData.package_type.enum"
                                                :description="formData.package_type.description"
                                                :readonly="formData.package_type.readonly"
                                                @click.native="clickField(formData.package_type)"
                                        ></field-with-errors>
                                    </div>
                                </div>

                                <product-basic-form
                                        :form-data="formData"
                                        :package-level-id="formData.package_level.value"
                                        ref="basicForm"
                                        :on-auto-fill-change="autoFill"
                                        @click-field="clickField($event)"
                                        :languages="languages"
                                        :language="language"
                                >
                                </product-basic-form>


                                <div class="row">
                                    <div class="col-md-6" style="color: red">
                                        {{ gettext('Fields marked with (*) are required.') }}
                                    </div>
                                </div>
                            </template>
                        </form-accordion>


                        <product-basic-form-options
                                :form-data="formData"
                                ref="basicFormOptions"
                                @click-field="clickField($event)"
                        >
                        </product-basic-form-options>

                        <product-location-form :form-data="formData"
                                               :server-errors="serverErrors"
                                               @click-field="clickField($event)"
                        >

                        </product-location-form>

                        <subproducts-form-edit :form-data="formData"
                                               :server-errors="serverErrors"
                                               v-if="formData.package_level.value != 70"
                                               @click-field="clickField($event)"
                                               ref='subproducts_form_edit'
                        >

                        </subproducts-form-edit>
                    </b-tab>
                    <b-tab :title="gettext('Measurements')" @click="locationHash='#/measurements'"
                           :active="locationHash === '#/measurements'" v-if="viewMask.measures.isAny">
                        <weights-dimensions-form
                                :form-data="formData"
                                :visible="true"
                                :server-errors="serverErrors"
                                @click-field="clickField($event)"
                        >
                        </weights-dimensions-form>
                    </b-tab>
                    <b-tab :title="gettext('Advanced')" @click="locationHash='#/advanced'"
                           :active="locationHash === '#/advanced'" v-if="advancedTab">
                        <div class="col-12">
                            <fieldset class='fieldset' id="gepir_fs_2">
                                <legend>
                                    {{ gettext('Optional information') }}
                                    <span style="font-size: 0.6em;vertical-align: middle;">&nbsp;</span>
                                </legend>
                            </fieldset>
                        </div>
                    </b-tab>
                    <b-tab :title="gettext('Picture')" @click="locationHash='#/picture'"
                           :active="locationHash === '#/picture'"
                           v-if="packageLevel >= 40 && packageLevel <= 70 && viewMask.picture">
                        <div id="picture" class="tab-pane">
                            <div class="row">
                                <div class="col-12">
                                    <div class="row">
                                        <div class="col-12">
                                            <picture-form :form-data="formData"
                                                          :visible="true"
                                                          :server-errors="serverErrors"
                                                          :edit="true"
                                                          @click-field="clickField($event)"
                                                          :languages="languages"
                                                          :language="language"
                                            >
                                            </picture-form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </b-tab>
                    <b-tab class="container-fluid"
                           :title="gettext('Symbols')"
                           @click="locationHash='#/symbols'"
                           :active="locationHash === '#/symbols'">
                        <!-- Barcodes generator -->
                        <div class="row">
                            <div class="col-12">
                                <barcode-generator-form :form-data="formData" :user="user"></barcode-generator-form>
                            </div>
                        </div>
                    </b-tab>

                    <b-tab :title="gettext('Summary')" @click="locationHash='#/summary'"
                           :active="locationHash === '#/summary'">
                        <div>
                            <product-summary :form-data="formData"
                                             :package-level="packageLevel"
                                             :gtin="gtin13"
                                             :gtin14="gtin14"
                                             :prefix="prefix"
                                             :language="language"
                                             :id="id.value"
                                             :package-type-name="packageTypeName">
                            </product-summary>
                        </div>
                    </b-tab>
                </b-tabs>
                <hr/>
            </form>
            <div class="row">
                <div class="col-4">
                    <div class="left-buttons-block">
                        <template v-if="prefixIsSpecial != 'READ-ONLY'">
                            <!-- temporary removed from the interface
                            <b-button variant="danger" @click.stop="$refs.deleteModal.open()">
                                {{ gettext('Delete') }}
                            </b-button>
                            -->
                            <b-button
                                    v-if="formData.package_level.value === 70 && mo_info.gs1_enable_clone_button"
                                    :href="`/products/${id.value}/duplicate/${targetMarketCode}/?fulledit_js=1`"
                                    variant="outline-secondary">
                                {{ gettext('Clone') }}
                            </b-button>

                            <makepack-modal
                                    :gtin="gtin"
                                    ref="makepackModal"
                                    @errors="handleAPIErrors($event)"
                            >
                            </makepack-modal>
                        </template>
                        <b-button v-if="formData.package_level.value > 30 && !mo_info.gs1_disable_hiearchy"
                                  variant="warning"
                                  @click.prevent="makepack_btn()">
                            {{ gettext('Make a Pack') }}
                        </b-button>
                    </div>
                </div>
                <div class="col-8">
                    <save-options
                            v-model="formData.gs1_cloud_state.value"
                            :form-data="formData"
                            :is-opted-out-allowed="mo_info.gs1_enable_cloud_opt_out"
                            :is-form-data-changed="isFormDataChanged"
                            :activate-disclaimer-text="mo_info.gs1_cloud_disclaimer"
                            :is-staff="is_staff"
                            :is-edit-form="true"
                            :is-loading="isSaving"
                            :package-level="formData.package_level.value"
                            @form-submit="submitForm"
                            @set-errors="handleAPIErrors($event)"
                    />
                </div>
            </div>
            <delete-modal :product-gtin="gtin" ref="deleteModal"></delete-modal>
            <message-modal :is-open="denyEditIsOpen"
                           :header="gettext('Message')"
                           @close="denyEditIsOpen = false"
            >
                <p>
                    {{gettext('You cannot edit a product field once activated. If the information is wrong place contact the')}}
                    <a target="_blank"
                       :href="mo_info.gs1_help_url_2">{{gettext('HELPDESK')}}</a>
                </p>
            </message-modal>
        </div>
        <spinner-indicator :loading="!loaded" class="main-spinner"></spinner-indicator>
    </div>
</template>

<script>
    import TokenService from '../../common/services/TokenService';
    import DeleteModal from './DeleteModal.vue';
    import FieldWithErrors from '../../common/components/FieldWithErrors';
    import ProductBasicForm from '../../common/components/ProductBasicForm';
    import ProductBasicFormOptions from '../../common/components/ProductBasicFormOptions';
    import ProductGeoForm from '../../common/components/ProductGeoForm';
    import WeightsDimensionsForm from '../../common/components/WeightsDimensionsForm';
    import PictureForm from '../../common/components/PictureForm';
    import SpinnerIndicator from "../../common/components/SpinnerIndicator";
    import APIService from '../../common/services/APIService';
    import TranslationService from '../../common/services/TranslationService';
    import ProductLocationForm from "../../common/components/ProductLocationForm";
    import FormAccordion from "../../common/components/FormAccordion";
    import SubproductsFormEdit from '../../common/components/SubproductsFormEdit';
    import ProductSummary from "../../common/components/Summary/ProductSummary";
    import MessageModal from "../../common/components/modals/MessageModal";
    import ProductTranslation from "../../common/components/Translation/ProductTranslation";
    import SaveOptions from "../../common/components/SaveOptions";
    import BarcodeGeneratorForm from "../../common/components/BarcodeGeneratorForm";
    import FormHelper from "../../common/helpers/FormHelper";
    import UomService from '../../common/services/UomService';
    import MakepackModal from '../../common/components/MakepackModal';


    require('formdata-polyfill');
    import _ from 'lodash';
    import GPCServices from "../../common/services/GPCServices";

    export default {
        data() {
            return {
                formData: {
                    "gtin": {
                        "title": gettext('Gtin'),
                        "description": "",
                        "type": "hidden",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "bar_placement": {
                        "title": gettext('Bar placement'),
                        "description": "",
                        "type": "hidden",
                        "errors": [],
                        "value": "/static/products/site/wizard/proddesc/BG.png",
                        "required": true,
                        "readonly": false
                    },
                    "package_level": {
                        "title": gettext('Package level'),
                        "description": "",
                        "type": "hidden",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "package_type": {
                        "title": gettext('Package type'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "dataById": {},
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "company": {
                        "title": gettext('Company'),
                        "description": "",
                        "type": "string",
                        "maxLength": 100,
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "label_description_i18n": {
                        "title": gettext('Label description'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "brand_i18n": {
                        "title": gettext('Brand'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "sub_brand": {
                        "title": gettext('Sub brand'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "functional_name_i18n": {
                        "title": gettext('Functional name'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "variant": {
                        "title": gettext('Variant'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "description_i18n": {
                        "title": gettext('Description'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "point_of_sale": {
                        "title": gettext('Point of sale'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "category": {
                        "title": gettext('Category'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "sku": {
                        "title": gettext('Sku'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "country_of_origin": {
                        "title": gettext('Country of origin'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "dataById": {},
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "target_market": {
                        "title": gettext('Target market'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "dataById": {},
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "language": {
                        "title": gettext('Language'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "dataById": {},
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "gln_of_information_provider": {
                        "title": gettext('Gln of information provider'),
                        "description": "",
                        "type": "string",
                        "errors": [],
                        "value": undefined,
                        "required": true,
                        "readonly": false
                    },
                    "is_bunit": {
                        "title": gettext('Is bunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "is_cunit": {
                        "title": gettext('Is cunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "is_dunit": {
                        "title": gettext('Is dunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "is_vunit": {
                        "title": gettext('Is vunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "is_iunit": {
                        "title": gettext('Is iunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "is_ounit": {
                        "title": gettext('Is ounit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "gross_weight": {
                        "title": gettext('Gross weight'),
                        "description": "",
                        "type": "number",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "gross_weight_uom": {
                        "title": gettext('Gross weight uom'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "net_weight": {
                        "title": gettext('Net weight'),
                        "description": "",
                        "type": "number",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "net_weight_uom": {
                        "title": gettext('Net weight uom'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "depth": {
                        "title": gettext('Depth'),
                        "description": "",
                        "type": "number",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "depth_uom": {
                        "title": gettext('Depth uom'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "width": {
                        "title": gettext('Width'),
                        "description": "",
                        "type": "number",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "width_uom": {
                        "title": gettext('Width uom'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "height": {
                        "title": gettext('Height'),
                        "description": "",
                        "type": "number",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "height_uom": {
                        "title": gettext('Height uom'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "image_i18n": {
                        "title": gettext('Image url'),
                        "description": "",
                        "type": "string",
                        "format": "uri",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "image_upload": {
                        "title": gettext('Image upload'),
                        "description": "",
                        "type": "file",
                        "format": "file",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "website_url": {
                        "title": gettext('Website URL'),
                        "description": "",
                        "type": "string",
                        "format": "uri",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "net_content": {
                        "title": gettext('Net content'),
                        "description": "",
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "net_content_uom": {
                        "title": gettext('Net content uom'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "gs1_cloud_state": {
                        "title": gettext('Gs1 cloud state'),
                        "description": "",
                        "type": "string",
                        "enum": [
                            ["DRAFT", gettext('DRAFT')],
                            ["ACTIVE", gettext('ACTIVE')],
                            ["INACTIVE", gettext('INACTIVE')],
                            ["OPTED_OUT", gettext('OPTED_OUT')],
                        ],
                        "errors": [],
                        "value": undefined,
                        "required": false,
                        "readonly": false
                    },
                    "subproducts": []
                },
                user: undefined,
                id: undefined,
                language: undefined,
                languages: undefined,
                mo_slug: undefined,
                mo_info: {},
                fallback_languages: [],
                product_template_id: undefined,
                product_template: undefined,
                loaded: false,
                tabIdx: 0,
                advancedTab: undefined,
                package: undefined,
                packageLevel: undefined,
                targetMarketCode: undefined,
                gtin: undefined,
                gtin_orig: undefined,
                gtin13: '',
                gtin14: '',
                gtin0: 0,
                kind: undefined,
                prefix: undefined,
                agreed: undefined,
                is_staff: undefined,
                userCompany: undefined,
                prefixIsSpecial: undefined,
                barcodeContent: '',
                isGlnAutoFill: false,
                cd: '',
                cloudLogTableData: {
                    columns: [
                        {title: gettext('Status'), field: 'rc'},
                        {title: gettext('Date'), field: 'time'}
                    ],
                    data: [],
                    total: 0,
                    query: {}
                },
                isAutoFill: false,
                subproduct_items: undefined,
                originalFormValues: {},  // changes tracking
                serverErrors: null,
                viewMask: null,
                denyEditIsOpen: false,
                allFieldErrors: [],
                isSaving: false,
                leadingReadonly: true
            };
        },
        computed: {
            locationHash: {
                get: function () {
                    return window.location.hash;
                },
                set: function (new_value) {
                    window.location.hash = new_value;
                }
            },
            packageTypeName() {
                const value = this.formData.package_type.dataById[_.parseInt(this.formData.package_type.value)];
                return value && value.name[this.language];
            },
            productLanguageSlug() {
                // return slug of the selected product language
                // in case if a language can't be detected, 'en' will be returned

                if (!this.formData.language.value || _.isEmpty(this.formData.language.dataById)) {
                    return 'en';
                }
                return this.formData.language.dataById[this.formData.language.value].slug;
            },
            isFormDataChanged() {
                // tracking form data changes
                let is_changed = false;

                _.forEach(this.originalFormValues, (originalValue, fieldName) => {
                    if (originalValue !== this.formData[fieldName].value) {
                        is_changed = true;
                        return false;
                    }
                });
                return is_changed;
            }
        },
        watch: {
            'formData.brand.value'() {
                this.autoFill();
            },
            'formData.sub_brand.value'(newVal, oldVal) {
                this.autoFill();
            },
            'formData.functional_name.value'() {
                this.autoFill();
            },
            'formData.variant.value'() {
                this.autoFill();
            },
            'formData.net_content.value'() {
                this.autoFill();
            },
            'formData.net_content_uom.value'() {
                this.autoFill();
            },
            'formData.package_type.value'(newVal) {
                if (newVal && this.formData.package_type.dataById[_.parseInt(newVal)]) {
                    this.formData.bar_placement.value = this.formData.package_type.dataById[_.parseInt(newVal)].image_url;
                }
            },
            'gtin'(newVal) {
                let result = 0;
                let core = newVal.substring(0, newVal.length - 1)
                for (let counter = core.length - 1; counter >= 0; counter--) {
                    if (counter % 2) {
                        result = result + parseInt(core.charAt(counter))
                    } else {
                        result = result + parseInt(core.charAt(counter)) * 3
                    }
                }
                let chk = (10 - (result % 10)) % 10;
                this.cd = chk

                //$this.$watch('gtin')()
                newVal = newVal.substring(0, newVal.length - 1) + chk
                this.gtin = newVal
            }
        },
        methods: {
            gettext(text) {
                return gettext(text);
            },
            pad(str, max) {
                str = str.toString();
                return str.length < max ? this.pad("0" + str, max) : str;
            },
            formatString(str, ...args) {
                return str.replace(/{(\d+)}/g, function (match, number) {
                    return typeof args[number] !== 'undefined' ? args[number] : match;
                });
            },
            autoFill() {
                if (this.$refs.basicFormOptions && this.$refs.basicForm.isAutoFill) {
                    let desc =
                        String(this.formData.brand.value || '') + ' ' + String(this.formData.sub_brand.value || '') +
                        ' ' + String(this.formData.functional_name.value || '') + ' ' +
                        String(this.formData.variant.value || '');
                    if (this.packageLevel === 70 && this.formData.net_content.value) {
                        this.formData.net_content_uom.enum.forEach(([key, value]) => {
                            if (key === this.formData.net_content.value) {
                                desc += ' ' + value;
                                return false;
                            }
                        });
                    }
                    this.formData.label_description.value = desc;
                }
            },
            GTINCheckDigit(s) {
                let result = 0;
                for (let counter = s.length - 1; counter >= 0; counter--) {
                    result = result + parseInt(s.charAt(counter)) * Math.pow(3, ((counter + 1) % 2));
                }
                return (10 - (result % 10)) % 10;
            },
            checkdigit() {
                let checkdigit;
                checkdigit = this.GTINCheckDigit(this.gtin[0] + this.pad(this.gtin13.replace(/\s+/g, ''), 13)
                    .substring(0, 12));
                return checkdigit;
            },
            submitForm() {
                this.isSaving = true;
                if (this.formData.package_level.value != 70) {
                    this.$refs.subproducts_form_edit.save_subproducts()
                }
                let gtin = this.formData.gtin.value;

                /*
                for (let subproduct in this.formData.subproducts) {
                    let subproduct_gtin = this.formData.subproducts[subproduct].gtin.value;
                    let subproduct_quantity = this.formData.subproducts[subproduct].quantity;
                    let subproduct_url = '/api/v1/products/' + gtin + '/subproducts/';
                    let subproductFormData = new FormData();
                    subproductFormData.set('subproduct', subproduct_gtin);
                    subproductFormData.set('quantity', subproduct_quantity);
                    this.$http.post(subproduct_url, subproductFormData).then();
                }
                */

                let productData = {
                    gtin: this.gtin,
                };
                if (this.formData.image_upload.value) {
                    productData['image_upload'] = this.formData.image_upload.value;
                }
                _.each([
                    'gln_of_information_provider', 'company', 'label_description_i18n', 'brand_i18n',
                    'sub_brand', 'functional_name_i18n', 'variant', 'description_i18n', 'category',
                    'sku', 'is_bunit', 'is_cunit', 'is_dunit', 'is_vunit', 'is_iunit', 'is_ounit',
                    'gross_weight', 'net_weight', 'depth', 'width', 'height', 'depth_uom', 'width_uom',
                    'height_uom', 'gross_weight_uom', 'net_weight_uom', 'net_content',
                    'net_content_uom', 'gs1_cloud_state', 'language', 'image_i18n', 'point_of_sale',
                    'website_url',
                ], key => {
                    this.formData[key].errors = [];
                    if (this.formData[key].value !== undefined && this.formData[key].value !== null) {
                        if (_.endsWith(key, '_i18n')) {
                            productData[key] = JSON.stringify(this.formData[key].value);
                        } else {
                            productData[key] = this.formData[key].value;
                        }
                    }
                });
                _.each(['package_type', 'package_level', 'country_of_origin', 'target_market'], key => {
                    if (!_.isNil(this.formData[key].value) && this.formData[key].value) {
                        productData[key] = _.parseInt(this.formData[key].value);
                    }
                });

                let productFormData = new FormData();
                _.forOwn(productData, (field_value, field_name) => {
                    productFormData.set(field_name, field_value);
                });
                let request_url = `/api/v1/products/${this.gtin_orig}/?template_id=${this.product_template_id}`;

                this.$http.patch(request_url, productFormData).then(response => {
                        if (_.hasIn(response, 'body.id.value')) {
                            // fixme: temporary solution with redirect to display summary
                            TokenService.redirect(`/products/${response.body.id.value}/fulledit_js/#summary`);
                            location.reload();
                        }
                    },
                    response => {
                        this.handleAPIErrors(response.body);

                    }
                ).finally(() => {
                    this.isSaving = false;
                })
            },
            initUser() {
                return this.$http.get(`/api/v1/accounts/login/`).then(response => {
                    if (_.isObject(_.get(response, 'body.user'))) {
                        this.user = response.body.user;
                        this.prefix = response.body.user.product_active_prefix.prefix;
                        this.agreed = response.body.user.agreed;
                        this.advancedTab = response.body.user.advanced_tab;
                        this.is_staff = response.body.user.is_staff;
                    }
                });
            },
            getTranslated(i18n_field, language) {
                return TranslationService.getTranslated(
                    i18n_field, language, this.fallback_languages
                );
            },
            loadI18nFields(response) {
                _.each(_.keys(this.formData), (fieldName) => {
                    if (_.endsWith(fieldName, '_i18n')) {
                        try {
                            this.formData[fieldName].value =
                                response.body[fieldName].value

                        }
                        catch (e) {
                            // console.log('exception in loadI18nFields', e);
                            this.formData[fieldName].value = undefined
                        }
                    }
                    // changes tracking
                    this.originalFormValues[fieldName] = this.formData[fieldName].value
                });
            },
            configureFields(api_response) {
                _.each(_.keys(this.formData), field_name => {
                    if (field_name === 'subproducts') {
                        return;
                    }
                    const field_parameters = api_response[field_name];

                    if (field_parameters && field_parameters.ui_enabled) {
                        this.formData[field_name].title = this.getTranslated(
                            JSON.parse(field_parameters.ui_label_i18n),
                            this.language
                        );
                        this.formData[field_name].required = field_parameters.ui_mandatory;
                        this.formData[field_name].readonly = field_parameters.ui_read_only;
                        if (field_parameters.definition_i18n) {
                            this.formData[field_name].description = this.getTranslated(
                                JSON.parse(field_parameters.definition_i18n),
                                this.language
                            );
                        }
                        else {
                            this.formData[field_name].description = field_parameters.definition;
                        }
                    } else {
                        // field is missing in config / marked as hidden
                        this.formData[field_name].type = 'hidden';
                    }
                });
            },

            handleAPIErrors: function (errors) {
                this.serverErrors = errors;
                console.log('API Error:', errors);
                this.allFieldErrors = [];
                if (typeof errors === 'string') {
                    this.allFieldErrors.push({
                        field: 'Internal Error',
                        text: 'Please contact Support'
                    })
                } else {
                    _.forOwn(errors, (field_errors, field_name) => {
                        let errors = null;
                        if (this.formData[field_name] && this.formData[field_name].type !== 'hidden') {
                            this.formData[field_name].errors = field_errors;
                            errors = field_errors.map((error) => {
                                return {
                                    field: this.formData[field_name].title,
                                    text: error
                                }
                            })
                        } else {
                            errors = field_errors.map((error) => {
                                return {
                                    field: field_name,
                                    text: error
                                }
                            })
                        }
                        this.allFieldErrors = this.allFieldErrors.concat(errors);

                    });
                }


                // reset gs1 cloud state to a previous if there are errors at a create step
                this.formData.gs1_cloud_state.value = this.originalFormValues.gs1_cloud_state;

                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            },
            loadGpc() {
                if (this.formData.category.type !== 'hidden' && this.formData.category.value && this.formData.category.value !== '') {
                    this.formData.category.loading = true;
                    this.formData = Object.assign({}, this.formData);
                    GPCServices.getList({
                        brick_code: this.formData.category.value
                    }).then(res => {
                        this.formData.category.selectedObject = res[0]
                    }).finally(() => {
                        this.formData.category.loading = false;
                        this.formData = Object.assign({}, this.formData);
                    })
                }
            },
            clickField(field) {
                if (field.readonly && this.formData.gs1_cloud_state.value === 'ACTIVE') {
                    this.denyEditIsOpen = true
                }
            },
            calculateCheckDigit() {
                this.gtin = this.gtin0 + this.gtin.substring(1)
            },
            makepack_btn() {
                console.log('makepack_btn');
                this.$refs.makepackModal.open();
            },
            changeLanguages(languages) {
                this.languages = languages
            },
            setActiveLanguage(language) {
                this.language = language
            }
        },
        mounted() {
            const gtin = document.getElementById('bcm-gtin').value;
            const FormAppDataEl = document.getElementById('FormAppData');
            const FormAppData = JSON.parse(FormAppDataEl.innerHTML);
            console.log(FormAppData)
            this.product_template_id = FormAppData.product_template_id;
            this.language = FormAppData.language;
            this.mo_slug = FormAppData['mo_slug'];
            APIService.getMemberOrganisation(this.mo_slug).then(
                mo_info => {
                    this.mo_info = mo_info;
                }
            );

            let request_url = `/api/v1/products/${gtin}/?template_id=${this.product_template_id}`;
            let productPromise = this.$http.get(request_url).then(response => {
                if (_.hasIn(response, 'body')) {
                    this.gtin = String(response.body.gtin.value);
                    this.gtin_orig = this.gtin;
                    this.gtin0 = this.gtin[0];
                    this.gtin13 = this.gtin.substring(1, 14);
                    this.gtin14 = this.gtin.substring(0, 14);
                    this.packageLevel = _.parseInt(response.body.package_level.value);
                    this.cd = this.gtin13[this.gtin13.length - 1];
                    this.formData.gtin.value = response.body.gtin.value;
                    this.formData.package_type.value = _.parseInt(response.body.package_type.value);
                    this.formData.package_level.value = _.parseInt(response.body.package_level.value);
                    this.id = response.body.id;

                    _.each([
                        ['country_of_origin', 'getCountries', ['id', 'name'], []],
                        ['target_market', 'getTargetMarkets', ['id', 'name', 'code'], []],
                        ['language', 'getLanguages', ['id', 'name', 'slug'], []],
                        ['package_type', 'getPackagingTypes', ['id', 'label_i18n'], [this.language, this.mo_slug]],
                    ], ([compKey, apiGetterName, fieldsList, parametersList]) => {
                        APIService[apiGetterName](...parametersList).then(list => {
                            this.formData[compKey].dataById = [];
                            this.formData[compKey].enum = _.map(list, (data) => {
                                this.formData[compKey].dataById[_.parseInt(data.id)] = data;
                                return _.map(fieldsList, fieldName => {
                                    if (_.endsWith(fieldName, '_i18n')) {
                                        return this.getTranslated(data[fieldName], this.language);
                                    } else {
                                        return data[fieldName];
                                    }
                                });
                            });
                            if (compKey === 'language') {
                                this.formData.language.value = _.parseInt(response.body.language.value);
                                this.loadI18nFields(response);
                            } else if (compKey === 'target_market') {
                                let field = this.formData[compKey];
                                this.targetMarketCode = field.dataById[field.value].code;
                            }
                        });
                        if (response.body[compKey]) {
                            this.formData[compKey].value = _.parseInt(response.body[compKey].value);
                        }
                    });

                    this.fallback_languages = FormAppData['fallback_languages'];
                    this.formData.language.value = FormAppData['form_data']['language'].value;

                    _.each([
                        'gln_of_information_provider', 'company', 'sub_brand', 'variant', 'category',
                        'sku', 'is_bunit', 'is_cunit', 'is_dunit', 'is_vunit', 'is_iunit', 'is_ounit',
                        'gross_weight', 'net_weight', 'depth', 'width', 'height', 'depth_uom',
                        'width_uom', 'height_uom', 'gross_weight_uom', 'net_weight_uom', 'net_content',
                        'net_content_uom', 'gs1_cloud_state', 'point_of_sale', 'website_url',
                    ], (fieldName) => {
                        try {
                            this.formData[fieldName].value = response.body[fieldName].value;
                        }
                        catch (e) {
                            this.formData[fieldName].value = undefined
                        }
                    });

                    _.forEach(this.formData, (field, fieldName) => {
                        // changes tracking, check this.loadI18nFields too
                        this.originalFormValues[fieldName] = this.formData[fieldName].value;
                    });

                    return response.body;
                }
            }).then((response_body) => {
                return this.configureFields(response_body);
            });

            Promise.all([this.initUser(), productPromise, this.packageLevel]).then(() => {
                this.loaded = true;
                this.viewMask = FormHelper.getViewMask(this.formData);
                if (this.viewMask.measures.isAny) {
                    UomService.getAllUom(this.viewMask).then((result) => {
                        FormHelper.fillFormUom(this.formData, result);
                    })
                }
                const uri = window.location.search.substring(1);
                const params = new URLSearchParams(uri);
                this.loadGpc();
            });

            this.kind = FormAppData['kind'];
            this.userCompany = FormAppData['user_company'];
            let barcodes = FormAppData['barcodes'];
            this.$watch(function () {
                if (this.gtin) {
                    return this.gtin[0];
                }
                return '';
            }, function () {
                this.cd = this.checkdigit();
            });
        },
        filters: {
            substring: function (value, from, to) {
                return value.substring(from, to);
            },
            split: function (value, str) {
                return value.split(str);
            },
            join: function (list, str) {
                return list.join(str);
            }
        },
        components: {
            BarcodeGeneratorForm,
            FieldWithErrors,
            DeleteModal,
            ProductBasicForm,
            ProductBasicFormOptions,
            ProductGeoForm,
            WeightsDimensionsForm,
            PictureForm,
            SpinnerIndicator,
            ProductLocationForm,
            SubproductsFormEdit,
            FormAccordion,
            ProductSummary,
            SaveOptions,
            MessageModal,
            MakepackModal,
            ProductTranslation
        }
    }

    function createbc() {
        console.log('Create bc')
    }
</script>

<style lang="scss">
    .ProductFullEdit {
        &--optionalFieldsError &-productOptions {
            color: #b94a48 !important;
            border: 1px solid #b94a48;
        }

        &--optionalFieldsError &-productOptionsLgd {
            color: #b94a48 !important;
        }
    }

    .main-spinner {
        margin-top: 150px;
        margin-bottom: 50px;
    }

    .hide-empty:empty {
        display: none;
    }

    .leading-control {
        display: inline;
        width: 15%;
        text-align: right;
        font-weight: bold;
        font-size: 1.5em;
        width: 5ch;
        height: 3em
    }

    .leading-control--readonly {
        text-align: center;
    }

</style>
