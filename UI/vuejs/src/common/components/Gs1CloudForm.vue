<template>
    <div class="row">
        <div class="col-12">
            <fieldset class="fieldset cloud_properties_fs">
                <legend>{{ gettext('Product properties') }}
                    <span style="font-size: 0.6em;vertical-align: middle;">
                    ({{ gettext('Must be present for the upload') }})&nbsp;
                </span>
                </legend>
                <div class="well">
                        <p>{{ gettext('Please note that the following attributes must be present for the product upload:') }}</p>
                        <ul>
                            <li>
                                <b>{{ gettext('gtin') }}:</b> {{ formData.gtin.value }}
                            </li>
                            <li>
                                <b>{{ gettext('target market') }}:</b> {{ target_market_name }}
                            </li>
                            <li>
                                <b>{{ gettext('brand') }}:</b> {{ formData.brand_i18n.value }}
                            </li>
                            <li>
                                <b>{{ gettext('label description') }}:</b> {{ formData.label_description_i18n.value }}
                            </li>
                            <li>
                                <b>{{ gettext('company name') }}:</b> {{ formData.company.value }}
                            </li>
                            <li>
                                <b>{{ gettext('category code') }}:</b> {{ formData.category.value }}
                            </li>
                            <li>
                                <b>{{ gettext('image') }}:</b> <a v-bind:href="formData.image_i18n.value" target="_blank">{{ image_name }}</a>
                            </li>
                            <li>
                                <b>{{ gettext('language') }}:</b> {{ language_name }}
                            </li>
                        </ul>
                        {{ gettext('To find out more click here') }}:
                        <a href="https://www.gs1ie.org/tools-services/data-services/gs1-cloud/">
                            https://www.gs1ie.org/tools-services/data-services/gs1-cloud/
                        </a>
                </div>
            </fieldset>

            <fieldset class="fieldset cloud_properties_fs">
                <legend>
                    {{ gettext('GS1 Cloud state') }}
                    <span style="font-size: 0.6em;vertical-align: middle;">
                    ({{ gettext('Must be active for synchronisation to take place') }})&nbsp;
                </span>
                </legend>
                <div class="well">
                    <div class="form-row">
                        <div class="col-6">
                            <field-with-errors
                                    :errors="formData.gs1_cloud_state.errors"
                                    v-model="formData.gs1_cloud_state.value"
                                    :disabled="opted_out_state"
                                    :label="gettext('Current state')" :name="'gs1_cloud_state'"
                                    :valuetype="formData.gs1_cloud_state.type"
                                    :choices="formData.gs1_cloud_state.enum">
                            </field-with-errors>
                        </div>
                        <div class="col-6">
                            <label style="margin: 36px 0 0 10px;">
                                <input type="checkbox" v-model="opted_out_state" />
                                {{ gettext('OPTED OUT') }}
                            </label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <label>{{ gettext('Last Status') }}</label>
                            <p>
                                <span v-if="gs1_cloud_last_status">{{ gs1_cloud_last_status }}<br/></span>
                                <span v-if="gs1_cloud_last_update">{{ gs1_cloud_last_update }}<br/></span>
                                <span v-else>Unavailable</span>
                            </p>
                        </div>
                    </div>
                </div>
            </fieldset>

            <fieldset class="fieldset cloud_properties_fs">
                <legend>
                    {{ gettext('GS1 Cloud audit') }}
                    <span style="font-size: 0.6em;vertical-align: middle;">
                    ({{ gettext('Log of the last operations') }})
                </span>
                </legend>
                <div class="well">
                    <!--
                        <datatable v-bind="cloudLogTableData"/>
                    -->
                </div>
            </fieldset>
        </div>
    </div>
</template>

<script>
    import _ from 'lodash';
    import FieldWithErrors from './FieldWithErrors';

    export default {
        components: {
            FieldWithErrors,
        },
        props: {
            formData: {
                required: true
            },
            visible: {
                required: false
            },
            serverErrors: {
                required: false,
                default: null
            }
        },
        data() {
            return {
                visibleModel: this.visible,
                target_market_name: '',
                language_name: '',
                gs1_cloud_last_status: '--',
                gs1_cloud_last_update: '--',
            };
        },
        computed: {
            image_name() {
                const MAX_LENGTH = 50;
                let image_name = this.formData.image_i18n.value;
                if(!image_name) {
                    return '';
                }
                if(image_name.length > MAX_LENGTH) {
                    image_name = '...' + image_name.substring(
                        image_name.length - MAX_LENGTH, image_name.length
                    );
                }
                return image_name;
            },
            opted_out_state: {
                get: function () {
                    return this.formData.gs1_cloud_state.value === 'OPTED_OUT';
                },
                set: function (new_value) {
                    if(this.opted_out_state) {
                        // todo: reset to this.gs1_cloud_last_status when it will be available
                        this.formData.gs1_cloud_state.value = 'DRAFT';
                    } else {
                        this.formData.gs1_cloud_state.value = 'OPTED_OUT';
                    }
                },
            }
        },
        methods: {
            gettext(text) {
                return gettext(text);
            },
            getNameFromFieldData(field) {
                if(field.value && !_.isEmpty(field.dataById)) {
                    return field.dataById[field.value].name;
                }
            },
        },
        watch: {
            'formData.target_market.enum': function (new_value, old_value) {
                // magic watch, waiting for async api data
                // 1. it's required to watch enum here
                //    (dataById will not work it seems it changes too quickly)
                // 2. we have to use old style function to have dotted syntax + "this"
                this.target_market_name = this.getNameFromFieldData(this.formData.target_market);
            },
            'formData.language.enum': function (new_value, old_value) {
                // magic watch, waiting for async api data
                // 1. it's required to watch enum here
                //    (dataById will not work it seems it changes too quickly)
                // 2. we have to use old style function to have dotted syntax + "this"
                this.language_name = this.getNameFromFieldData(this.formData.language);
            },
        },
        mounted() {
            // console.log('formData', this.formData);
        }
    }
</script>

<style scoped>

</style>
