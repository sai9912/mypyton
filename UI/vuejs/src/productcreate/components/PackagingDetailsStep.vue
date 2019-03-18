<template>
    <div>

        <form method="post" enctype="multipart/form-data" id="detailsform" class="ProductFullEdit"
              :class="{
              'ProductFullEdit--optionalFieldsError': $refs.basicFormOptions ?
              $refs.basicFormOptions.optionalFieldsError:false}"
              ref="ProductFullEdit"
              v-if="!loading">

            <b-alert show variant="danger" v-for="error in nonFieldErrors">
                <strong>{{error.field}}: </strong>{{ error.text }}
            </b-alert>
            <form-accordion :visible="true">
                <template slot="header">{{ gettext('Product Identification') }}</template>
                <template slot="body">
                    <product-basic-form
                            :form-data="formData"
                            :package-level-id="packageLevelId"
                            :auto-fill-default="true"
                            ref="basicForm">
                    </product-basic-form>
                    <div class="row">
                        <div class="col-md-6" style="color: red">
                            {{ gettext('Fields marked with (*) are required.') }}
                        </div>
                    </div>
                </template>
            </form-accordion>

            <product-basic-form-options :form-data="formData" ref="basicFormOptions"
                                        :server-errors="serverErrors">
            </product-basic-form-options>

            <product-location-form :form-data="formData"
                                   :gln-value="$store.state.ProductCreation.gln_of_information_provider"
                                   :server-errors="serverErrors"></product-location-form>

            <weights-dimensions-form :form-data="formData" :server-errors="serverErrors"></weights-dimensions-form>
            <picture-form :form-data="formData" :server-errors="serverErrors"></picture-form>
            <subproducts-form
                v-if="packageLevelId !== 70"
                :form-data="formData"
                :server-errors="serverErrors">
            </subproducts-form>

            <div class="row mt-2">
                <div class="col-6">
                    <div class="left-buttons-block">
                        <a class='btn btn-default' @click.prevent="prev">{{ gettext('Previous') }}</a>
                    </div>
                </div>

                <div class="col-6">
                    <save-options
                            v-model="formData.gs1_cloud_state.value"
                            :form-data="formData"
                            :is-form-data-changed="true"
                            :is-opted-out-allowed="this.$store.state.ProductCreation.moInfo.gs1_enable_cloud_opt_out"
                            :activate-disclaimer-text="this.$store.state.ProductCreation.moInfo.gs1_cloud_disclaimer"
                            :is-loading="isSaving"
                            :package-level="packageLevelId"
                            @form-submit="save"
                            @set-errors="handleAPIErrors($event)"
                    />
                </div>
            </div>
        </form>

        <spinner-indicator :loading="loading" class="main-spinner"></spinner-indicator>
    </div>


</template>

<script>
    import {mapActions} from 'vuex';
    import ProductBasicForm from '../../common/components/ProductBasicForm';
    import ProductBasicFormOptions from '../../common/components/ProductBasicFormOptions';
    import ProductGeoForm from '../../common/components/ProductGeoForm';
    import WeightsDimensionsForm from '../../common/components/WeightsDimensionsForm';
    import PictureForm from '../../common/components/PictureForm';
    import SubproductsForm from '../../common/components/SubproductsForm';
    import APIService from '../../common/services/APIService';
    import FieldWithErrors from '../../common/components/FieldWithErrors';
    import SpinnerIndicator from "../../common/components/SpinnerIndicator";
    import ProductLocationForm from "../../common/components/ProductLocationForm";
    import FormAccordion from "../../common/components/FormAccordion";
    import ProductTranslation from "../../common/components/Translation/ProductTranslation"
    import TranslationService from '../../common/services/TranslationService';
    import SaveOptions from "../../common/components/SaveOptions";
    import _ from 'lodash';
    import UomService from "../../common/services/UomService";
    import FormHelper from "../../common/helpers/FormHelper";

    require('formdata-polyfill');

    export default {
        data() {
            return {
                formData: {
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
                        "required": false,
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
                        "value": "",
                        "required": false,
                        "readonly": false
                    },
                    "is_bunit": {
                        "title": gettext('Is bunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": true,
                        "required": false,
                        "readonly": false
                    },
                    "is_cunit": {
                        "title": gettext('Is cunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": true,
                        "required": false,
                        "readonly": false
                    },
                    "is_dunit": {
                        "title": gettext('Is dunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": false,
                        "required": false,
                        "readonly": false
                    },
                    "is_vunit": {
                        "title": gettext('Is vunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": false,
                        "required": false,
                        "readonly": false
                    },
                    "is_iunit": {
                        "title": gettext('Is iunit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": false,
                        "required": false,
                        "readonly": false
                    },
                    "is_ounit": {
                        "title": gettext('Is ounit'),
                        "description": "",
                        "type": "boolean",
                        "errors": [],
                        "value": false,
                        "required": false,
                        "readonly": false
                    },
                    "country_of_origin": {
                        "title": gettext('Country of origin'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": 103,
                        "required": false,
                        "readonly": false
                    },
                    "target_market": {
                        "title": gettext('Target market'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": 103,
                        "required": false,
                        "readonly": false
                    },
                    "language": {
                        "title": gettext('Language'),
                        "description": "",
                        "type": "string",
                        "enum": [],
                        "errors": [],
                        "value": 1,
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
                    "package_level": {
                        "title": gettext('Package level'),
                        "description": "",
                        "type": "hidden",
                        "errors": [],
                        "value": _.parseInt(this.$store.state.ProductCreation.packageLevel),
                        "required": false,
                        "readonly": false
                    },
                    "package_type": {
                        "title": gettext('Package type'),
                        "description": "",
                        "type": "hidden",
                        "errors": [],
                        "value": _.parseInt(this.$store.state.ProductCreation.packageType),
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
                    "image_i18n": {
                        "title": gettext('Image url'),
                        "description": "",
                        "type": "string",
                        "format": "uri",
                        "errors": [],
                        "value": "/static/site/img/no-image.gif",
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
                        "value": 'DRAFT',
                        "required": false,
                        "readonly": false
                    },
                },
                defaultPromise: null,
                nonFieldErrors: [],
                loading: true,
                serverErrors: null,
                packageType: 1,
                viewMask: null,
                isSaving: false
            };
        },
        computed: {
            gtin: {
                get() {
                    return this.$store.state.ProductCreation.gtin;
                },
                set(val) {
                    this.$store.commit('ProductCreation/setGtin', val);
                }
            },
            packageLevelId: {
                get() {
                    return _.parseInt(this.$store.state.ProductCreation.packageLevel)
                },
                set(val) {
                    this.$store.commit('ProductCreation/setPackageLevel', val);
                }
            },
            productTemplateId: {
                get() {
                    return _.result(_.find(
                        this.$store.state.ProductCreation.packageLevelList,
                        item => item.id === this.packageLevelId
                    ), 'template_id', null);
                }
            },
            languageSlug() {
                return this.$store.state.ProductCreation.language || 'en';
            },
            productLanguageSlug() {
                // return slug of the selected product language
                // in case if a language can't be detected, 'en' will be returned
                let langs_data = this.formData.language.dataById;
                let lang_value = this.formData.language.value;

                if (!lang_value || _.isEmpty(langs_data) || !langs_data[lang_value]) {
                    return 'en';
                }

                return langs_data[lang_value].slug;
            },
        },
        watch: {
            'productTemplateId'(new_value, old_value) {
                this.configureFields();
            },
            '$store.state.ProductCreation.gln_of_information_provider' (val) {
                // required for subproducts when store is not loaded yet
                this.formData.gln_of_information_provider.value = val;
            }
        },
        methods: {
            ...mapActions({
                next: 'ProductCreation/nextStep',
                prev: 'ProductCreation/prevStep',
                showSummaryData: 'ProductCreation/showSummaryData',
            }),
            gettext(text) {
                return gettext(text);
            },
            getTranslated(i18n_field) {
                return TranslationService.getTranslated(
                    i18n_field, this.languageSlug, this.fallback_languages
                );
            },
            configureFields() {
                if (!this.$store.state.ProductCreation.packageLevelList.length) {
                    return;
                }
                this.defaultPromise.finally(() => {
                    APIService.getTemplateWithAttributes(this.productTemplateId).then(template => {
                        let attributes = template.attributes;
                        let attributes_parameters = {};
                        _.each(attributes, attribute => {
                            attributes_parameters[attribute.path.split('.').pop()] = attribute;
                        });
                        _.each(_.keys(this.formData), field_name => {
                            const attribute_parameters = attributes_parameters[field_name];
                            if (attribute_parameters && attribute_parameters.ui_enabled) {
                                this.formData[field_name].title = this.getTranslated(
                                    JSON.parse(attribute_parameters.ui_label_i18n)
                                );
                                this.formData[field_name].required = attribute_parameters.ui_mandatory;
                                this.formData[field_name].readonly = attribute_parameters.ui_read_only;
                                if (attribute_parameters.definition_i18n) {
                                    this.formData[field_name].description = this.getTranslated(
                                        JSON.parse(attribute_parameters.definition_i18n)
                                    );
                                }
                                else {
                                    this.formData[field_name].description = attribute_parameters.definition;
                                }

                            } else {
                                // field is missing in config / marked as hidden
                                this.formData[field_name].type = 'hidden';
                            }
                        });

                        this.viewMask = FormHelper.getViewMask(this.formData);
                        if (this.viewMask.measures.isAny) {
                            UomService.getAllUom(this.viewMask).then((result) => {
                                FormHelper.fillFormUom(this.formData, result);
                            })
                        }

                    }).finally(() => {
                        this.loading = false;
                    });
                })


            },
            handleAPIErrors(errors) {
                console.log('API Error:', errors);
                this.serverErrors = errors;
                this.nonFieldErrors = [];
                if (typeof errors === 'string') {
                    this.nonFieldErrors.push({
                        field: 'Internal Error',
                        text: 'Please contact Support'
                    })
                } else {
                    _.forOwn(errors, (field_errors, field_name) => {
                        if (this.formData[field_name] && this.formData[field_name].type !== 'hidden') {
                            this.formData[field_name].errors = field_errors;
                        } else {
                            const errors = field_errors.map((error) => {
                                return {
                                    field: field_name,
                                    text: error
                                }
                            });
                            this.nonFieldErrors = this.nonFieldErrors.concat(errors);
                        }
                    });
                }


                // reset gs1 cloud state to "DRAFT" if there are errors at a create step
                this.formData.gs1_cloud_state.value = 'DRAFT';
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            },
            changeLanguages(languages) {
                this.languages = languages
            },
            setActiveLanguage(language) {
                this.language = language
            },
            save() {
                this.isSaving = true;
                let postData = {
                    // gtin: this.$store.state.ProductCreation.gtin,
                    gtin: this.gtin,
                    gs1_company_prefix: this.$store.state.ProductCreation.gcp,
                };
                if (this.formData.image_upload.value) {
                    postData['image_upload'] = this.formData.image_upload.value;
                }


                _.forEach([
                    'company', 'category', 'label_description_i18n', 'description_i18n', 'brand_i18n',
                    'sub_brand', 'functional_name_i18n', 'variant', 'is_bunit', 'is_cunit', 'is_dunit',
                    'is_vunit', 'is_iunit', 'is_ounit', 'country_of_origin', 'website_url',
                    'depth', 'depth_uom', 'width', 'width_uom', 'height', 'height_uom',
                    'gross_weight', 'gross_weight_uom', 'net_weight', 'net_weight_uom', 'language',
                    'image_i18n', 'package_level', 'package_type', 'gln_of_information_provider',
                    'sku', 'net_content', 'net_content_uom', 'point_of_sale', 'gs1_cloud_state',
                ], (key) => {
                    if (this.formData[key]) {
                        this.formData[key].errors = [];
                        if (this.formData[key].value !== undefined) {
                            if (_.endsWith(key, '_i18n')) {
                                postData[key] = JSON.stringify(
                                    {[this.productLanguageSlug]: this.formData[key].value}
                                );
                            } else {
                                postData[key] = this.formData[key].value;
                            }
                        }

                    }
                });
                _.forEach(['country_of_origin', 'target_market', 'language'], key => {
                    if (this.formData[key].value) {
                        postData[key] = _.parseInt(this.formData[key].value);
                    } else {
                        // don't send empty values to have an ability receive correct error messages
                        // like "this field is required"
                        delete postData[key];
                    }
                });
                let prefix = postData.gs1_company_prefix;
                let template_name = _.result(_.find(this.$store.state.ProductCreation.packageLevelList,
                    item => item.id === this.packageLevelId
                ), 'name', '');
                let request_url = `/api/v1/prefixes/${prefix}/products?template_name=${template_name}`;

                let productFormData = new FormData();
                _.forOwn(postData, (field_value, field_name) => {
                    productFormData.set(field_name, field_value);
                });
                let args = document.location.href.match(/package_level=(\d+)&package_type=(\d+)/);
                if (args) {
                    postData['package_level'] = args[1];
                    postData['package_type'] = args[2];
                    productFormData.set('package_level', args[1]);
                    productFormData.set('package_type', args[2]);
                }

                this.$http.post(request_url, productFormData).then(
                    response => {
                        this.gtin = _.get(response, 'body.gtin.value', undefined);
                        for (let subproduct in this.$store.state.ProductCreation.subproducts) {
                            let subproduct_gtin = this.$store.state.ProductCreation.subproducts[subproduct].gtin.value;
                            let subproduct_count = this.$store.state.ProductCreation.subproducts[subproduct].count;
                            let subproduct_url = `/api/v1/products/${this.gtin}/subproducts/`;
                            let subproductFormData = new FormData();
                            subproductFormData.set('subproduct', subproduct_gtin);
                            subproductFormData.set('quantity', subproduct_count);
                            this.$http.post(subproduct_url, subproductFormData).then(
                                response => { /* debug here if required */ }
                            );
                        }

                        this.showSummaryData({
                            result: response.body,
                            formData: this.formData,
                        })
                    },
                    (response) => {
                        this.handleAPIErrors(response.body);
                    }
                ).finally(() => {
                    this.isSaving = false;
                });
            }
        },
        components: {
            ProductBasicForm,
            ProductBasicFormOptions,
            ProductGeoForm,
            WeightsDimensionsForm,
            PictureForm,
            SubproductsForm,
            FieldWithErrors,
            SpinnerIndicator,
            ProductLocationForm,
            FormAccordion,
            SaveOptions,
            ProductTranslation
        },
        mounted() {
            this.loading = true;
            if (this.$route.query) {
                if (this.$route.query.package_level) {
                    this.packageLevelId = parseInt(this.$route.query.package_level);
                }
                if (this.$route.query.package_type) {
                    this.$store.commit('ProductCreation/setPackageType', parseInt(this.$route.query.package_type));
                }
            }

            this.formData.gln_of_information_provider.value = this.$store.state.ProductCreation.gln_of_information_provider;

            let countries_promise = APIService.getCountries().then(countryList => {
                this.formData.country_of_origin.enum = _.map(countryList, ({id, code, name}) => {
                    return [id, name];
                });
                this.formData.country_of_origin.enum.splice(0, 0, [null, '-----']);
            });
            let target_market_promise = APIService.getTargetMarkets().then(marketList => {
                this.formData.target_market.enum = _.map(marketList, ({id, name}) => {
                    return [id, name];
                });
                this.formData.target_market.enum.splice(0, 0, [null, '-----']);
            });
            let language_promise = APIService.getLanguages().then(languageList => {
                this.formData.language.dataById = [];
                this.formData.language.enum = _.map(languageList, (data) => {
                    this.formData.language.dataById[_.parseInt(data.id)] = data;
                    return [data.id, data.name, data.slug];
                });
                this.formData.language.enum.splice(0, 0, [null, '-----', '']);
            });
            this.defaultPromise = Promise.all([countries_promise, target_market_promise, language_promise]).then(() => {
                APIService.getDefaults().then(defaults => {
                    this.formData.country_of_origin.value = defaults.country_of_origin || null;
                    this.formData.target_market.value = defaults.target_market || null;
                    this.formData.language.value = defaults.language || null;
                });
            });
            this.configureFields();
        }

    }
</script>

<style scoped>
    .main-spinner {
        margin-top: 150px;
        margin-bottom: 50px;
    }

    .left-buttons-block {
        position: absolute;
        bottom: 0;
    }
</style>
