<template>
    <div class="mt-3">

        <!--
        <div class='button-container'>
            <a class='btn btn-primary' target="_blank"
               :href="'/products/'+id+'/print_summary/'">
                {{gettext('Print Product Summary')}}
            </a>
        </div>
        <hr/>
        -->

        <div class="mt-3 mb-3">
            <template v-if="gtin14">
            <div class="summary-main row">
                <div class=" col-4 summary-main-title">
                    {{gettext('GTIN-13 Number')}}:
                </div>
                <div class=" col-auto summary-main-value">
                    <a :href="'/products/'+id+'/fulledit_js/'" v-if="showLink">{{gtin14}}</a>
                    <span v-else>{{gtin14}}</span>
                </div>
            </div>
            </template>
            <div class="summary-main row">
                <div class="col-4  summary-main-title">
                    {{gettext('GS1 Company Prefix')}}:
                </div>
                <div class=" col-auto summary-main-value">

                    {{prefix}}
                </div>
            </div>
            <div class="summary-main row">
                <div class="col-4  summary-main-title">
                    {{ formData.package_type.title }}:
                </div>
                <div class=" col-auto summary-main-value">
                    {{packageTypeName}}
                </div>
            </div>
        </div>


        <div class="summary-block">

            <div class="summary-header">
                {{gettext('Basic')}}
            </div>
            <div class="summary-content">


                <summary-field
                    :field="formData.company"
                >

                </summary-field>

                <summary-field
                    v-if="formData.package_level.value === 70 || formData.package_level.value === '70'"
                    :field="formData.label_description_i18n"
                >
                </summary-field>

                <summary-field
                    v-if="false"
                    :field="formData.gs1_company_prefix"
                >

                </summary-field>


                <summary-field

                    :field="formData.gln_of_information_provider"
                >

                </summary-field>

                <summary-field

                    :field="formData.brand_i18n"
                >

                </summary-field>

                <summary-field

                    :field="formData.sub_brand"
                >

                </summary-field>
                <summary-field

                    :field="formData.functional_name_i18n"
                >

                </summary-field>
                <summary-field

                    :field="formData.variant"
                >

                </summary-field>
                <summary-field

                    :field="formData.description_i18n"
                >

                </summary-field>
                <summary-field
                    :title="formData.category.title"
                    :field="formData.category"
                    :value="formData.category.selectedObject?formData.category.selectedObject.Brick + ' ('+formData.category.selectedObject.BrickCode + ')':''"
                >

                </summary-field>
                <summary-field
                    :field="formData.sku"
                >

                </summary-field>


                <summary-field

                    :field="formData.country_of_origin"
                >

                </summary-field>


                <summary-field

                    :field="formData.target_market"
                >

                </summary-field>
                <summary-field

                    :field="formData.language"
                >
                </summary-field>
            </div>

        </div>


        <div class="summary-block" v-if="viewMask.measures.isAny">

            <div class="summary-header">
                {{gettext('Measurements')}}
            </div>

            <div class="summary-content">
                <summary-field
                    :title="formData.net_content.title"
                    :field="formData.net_content"
                    :uom="formData.net_content_uom"
                >

                </summary-field>

                <summary-field
                    :title="gettext('Product')+' '+formData.gross_weight.title"
                    :field="formData.gross_weight"
                    :uom="formData.gross_weight_uom"
                >

                </summary-field>
                <summary-field
                    :title="gettext('Product')+' '+formData.net_weight.title"
                    :field="formData.net_weight"
                    :uom="formData.net_weight_uom"
                >

                </summary-field>
                <summary-field
                    :title="gettext('Product')+' '+formData.depth.title"
                    :field="formData.depth"
                    :uom="formData.depth_uom"
                >

                </summary-field>
                <summary-field
                    :title="gettext('Product')+' '+ formData.width.title"
                    :field="formData.width"
                    :uom="formData.width_uom"
                >

                </summary-field>
                <summary-field
                    :title="gettext('Product')+' '+formData.height.title"
                    :field="formData.height"
                    :uom="formData.height_uom"
                >

                </summary-field>
            </div>


        </div>

        <div class="summary-block" v-if="packageLevel >= 40 && packageLevel <= 70  && viewMask.picture">

            <div class="summary-header">
                {{gettext('Picture')}}
            </div>
            <div class="summary-content">
                <summary-field :field="formData.image_i18n" :value="fileName">
                </summary-field>

                <div>
                    <div class="thumbnail">
                        <img :src="imageSrc">
                    </div>
                </div>
            </div>
        </div>

        <!--<hr/>-->

        <div class='button-container'>
            <!--
                <a class='btn btn-primary' target="_blank"
                   :href="'/products/'+id+'/print_summary/'">
                    {{ gettext('Print Product Summary') }}
                </a>
            -->
            <div class='float-right' v-if="finish">
                <a class='btn btn-primary'
                   href="/products/js-list?sort_mode=desc&sort_field=created">{{ gettext('Finish') }}</a>
            </div>
        </div>

    </div>

</template>

<script>
    import SummaryField from "./SummaryField"
    import FormHelper from "../../helpers/FormHelper";
    import TranslationService from '../../services/TranslationService';
    import * as _ from "lodash";

    export default {
        name: "ProductSummary",
        components: {
            SummaryField
        },
        props: {
            packageLevel: {
                required: true
            },
            formData: {
                required: true
            },
            responseData: {
                required: false
            },
            finish: {
                required: false,
                default: false
            },
            gtin: {
                required: true
            },
            gtin14: {
                required: false,
                default: ''
            },
            prefix: {
                required: true
            },
            language: {
                required: true
            },
            id: {
                required: true
            },
            packageTypeName: {
                required: true
            },
            showLink: {
                required: false,
                default: false

            }
        },
        data() {
            return {}
        },
        methods: {
            gettext(text) {
                return gettext(text)
            }
        },
        computed: {
            viewMask() {
                return FormHelper.getViewMask(this.formData)
            },
            imageSrc() {
                if (this.formData.image_i18n.value) {
                    return this.formData.image_i18n.value;
                } else if (this.responseData && this.responseData.image_i18n.value) {
                    return TranslationService.getTranslated(
                        this.responseData.image_i18n.value,
                        this.language,
                    );
                } else {
                    return '/static/site/img/no-image.gif';
                }
            },
            fileName() {
                if (this.formData.image_i18n.value) {
                    const parts = this.formData.image_i18n.value.split('/');
                    return parts[parts.length - 1]
                }
                return ''
            }
        }
    }
</script>

<style scoped>
    .summary-header {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .summary-block {
        margin-bottom: 20px;
    }

    .summary-content {
        padding-left: 20px;
    }

    .summary-main-title {
        font-weight: 600;
        font-size: 16px;
    }

    .summary-main-value {
        font-weight: 300;
        font-size: 16px;
    }
</style>
