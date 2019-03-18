<template>
    <div>

        <form-accordion :visible="false" class="mb-3">
            <template slot="header">

                <div class="row justify-content-between w-100">
                    <div class="col-auto">
                        {{gettext('Translation')}}
                    </div>
                    <div class="col-auto" v-if="activeLanguage">
                        <span>{{gettext('Currently Selected')}}: </span>
                        {{activeLanguage.name}}
                    </div>
                </div>
            </template>
            <template slot="body">

                <div class="active-languages">
                    <label class="control-label" for="selectAddLanguage">
                        Currently added languages
                    </label>
                    <div v-for="item in addedLanguages">
                        <form-accordion :visible="false" class="mb-3 mt-1" :small="true">
                            <template slot="header">
                                <div class="row justify-content-between w-100 align-items-center language-header">
                                    <div class="col-auto">
                                        <div>{{item.name}}</div>
                                    </div>
                                    <div class="col-auto" v-if="activeLanguage">
                                        <span class="text-dark mr-2"
                                              v-if="activeLanguage === item">{{gettext('Selected')}}</span>

                                        <button class="btn btn-primary   btn-sm" v-if="activeLanguage !== item"
                                                @click.prevent.stop="setActive(item)">Set Active
                                        </button>

                                        <button class="btn btn-danger   btn-sm" :disabled="!moreThanOne"
                                                @click.prevent.stop="removeLanguage(item)">Remove
                                        </button>
                                    </div>
                                </div>
                            </template>
                            <template slot="body">
                                <div class="row">
                                    <div class="col-9 hide-empty"
                                         v-if="packageLevelId === 70 || packageLevelId === '70'">
                                        <field-with-errors
                                                :errors="formData.label_description_i18n.errors"
                                                v-model="formData.label_description_i18n.value"
                                                :label="formData.label_description_i18n.title"
                                                :name="'label_description_i18n'"
                                                :required="formData.label_description_i18n.required"
                                                :valuetype="formData.label_description_i18n.type"
                                                :description="formData.label_description_i18n.description"
                                                :readonly="formData.label_description_i18n.readonly"
                                                @click.native="click(formData.label_description_i18n)"
                                                :languages="addedLanguages"
                                                :language="item.code"
                                        >
                                        </field-with-errors>
                                    </div>
                                    <div class='col-6 hide-empty'>
                                        <field-with-errors
                                                :errors="formData.brand_i18n.errors"
                                                v-model="formData.brand_i18n.value"
                                                :label="formData.brand_i18n.title"
                                                :name="'brand_i18n'"
                                                :required="formData.brand_i18n.required"
                                                :valuetype="formData.brand_i18n.type"
                                                :description="formData.brand_i18n.description"
                                                :readonly="formData.brand_i18n.readonly"
                                                @click.native="click(formData.brand_i18n)"
                                                :languages="addedLanguages"
                                                :language="item.code"
                                        ></field-with-errors>
                                    </div>
                                    <div class='col-6 hide-empty'>
                                        <field-with-errors
                                                :errors="formData.functional_name_i18n.errors"
                                                v-model="formData.functional_name_i18n.value"
                                                :label="formData.functional_name_i18n.title"
                                                :name="'functional_name_i18n'"
                                                :required="formData.functional_name_i18n.required"
                                                :valuetype="formData.functional_name_i18n.type"
                                                :description="formData.functional_name_i18n.description"
                                                :readonly="formData.functional_name_i18n.readonly"
                                                @click.native="click(formData.functional_name_i18n)"
                                                :languages="addedLanguages"
                                                :language="item.code"
                                        ></field-with-errors>
                                    </div>
                                    <div class="col-6 hide-empty">
                                        <field-with-errors
                                                :errors="formData.image_i18n.errors"
                                                v-model="formData.image_i18n.value"
                                                :label="formData.image_i18n.title"
                                                :name="'image_i18n'"
                                                :required="formData.image_i18n.required"
                                                :valuetype="formData.image_i18n.type"
                                                :description="formData.image_i18n.description"
                                                :readonly="formData.image_i18n.readonly"
                                                @click.native="click(formData.image_i18n)"
                                                :languages="addedLanguages"
                                                :language="item.code"
                                        >
                                        </field-with-errors>
                                    </div>

                                    <description-field class="col-12" :form-data="formData"
                                                       :languages="addedLanguages"
                                                       :language="item.code"
                                                       @click-field="click($event)"/>


                                </div>


                            </template>
                        </form-accordion>
                    </div>
                </div>
                <div class="mt-4">
                    <label class="control-label" for="selectAddLanguage">
                        Select language for adding to list
                    </label>

                    <v-select id="selectAddLanguage"
                              :value="value"
                              :placeholder="gettext('Add language')"
                              @input="addLanguage($event)"
                              label="name"
                              :options="nonAddedLanguages"></v-select>


                </div>
            </template>
        </form-accordion>
    </div>
</template>

<script>
    import FormAccordion from '../FormAccordion';
    import FieldWithErrors from '../FieldWithErrors';
    import DescriptionField from "../fields/DescriptionField"
    import vSelect from 'vue-select'
    import * as _ from "lodash"

    export default {
        components: {
            FormAccordion,
            vSelect,
            FieldWithErrors,
            DescriptionField
        },
        data() {
            return {
                addedLanguages: [],
                nonAddedLanguages: [],
                activeLanguage: null,
                value:
                    null
            }
                ;
        },
        computed: {
            moreThanOne() {
                return this.addedLanguages.length > 1;
            }
        },
        methods: {
            click(form) {
                this.$emit('click-field', form)
            },
            gettext(text) {
                return gettext(text)
            },
            getValue() {
                return null;
            },
            addLanguage(item) {
                if (item) {
                    this.value = item;
                    this.addedLanguages.push(item);
                    this.nonAddedLanguages.splice(this.nonAddedLanguages.indexOf(item), 1)
                    this.$emit('change', Object.assign([], this.addedLanguages))
                    setTimeout(() => {
                        this.value = null
                    }, 0)
                }

            },
            removeLanguage(item) {
                this.addedLanguages.splice(this.addedLanguages.indexOf(item), 1)
                this.nonAddedLanguages.push(item);
                if (item === this.activeLanguage) {
                    this.activeLanguage = this.addedLanguages[0]
                }
                this.$emit('change', Object.assign([], this.addedLanguages));
            },
            setActive(item) {
                this.activeLanguage = item;
                this.$emit('set-active', item.code);
            }
        },
        props: {
            formData: {
                required: true
            },
            languages: {
                required: true
            },
            currentLanguage: {
                required: true
            }
        },
        mounted() {

            const languages = this.languages.filter(item => item[2]).map(item => {
                return {
                    code: item[2],
                    name: item[1]
                }
            });

            const fisrti18n = Object.keys(this.formData).find((key) => {
                return _.endsWith(key, '_i18n') && this.formData[key].value && this.formData[key].type !== 'hidden'
            });

            let currentLanguageKeys = [];
            if (!fisrti18n) {
                currentLanguageKeys = [this.currentLanguage]
            }
            else {
                currentLanguageKeys = Object.keys(this.formData[fisrti18n].value);
            }
            this.addedLanguages = languages.filter((item) => {
                return currentLanguageKeys.find((code) => code === item.code)
            });
            this.nonAddedLanguages = languages.filter((item) => {
                return !currentLanguageKeys.find((code) => code === item.code)
            });
            this.activeLanguage = this.addedLanguages.find((item) => item.code === this.currentLanguage);
            if (!this.activeLanguage) {
                this.activeLanguage = languages.find((item) => item.code === this.currentLanguage);
                this.addedLanguages.push(this.activeLanguage);
            }


            this.$emit('change', Object.assign([], this.addedLanguages))

        }
    }
</script>

<style>
    .language-header {
        height: 32px;
    }

    .active-languages .collapse-block {
        margin-top: 0px !important;
    }
</style>
