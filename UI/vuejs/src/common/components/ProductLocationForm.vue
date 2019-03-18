<template>


    <form-accordion :visible="visible" v-if="isGeoBlockShowed || formData.gln_of_information_provider.type!=='hidden' ">
        <template slot="header">
            <span>{{ gettext('Location information') }}</span>
        </template>
        <template slot="body">
            <div class="row">
                <div class="col-12">
                    <product-geo-form :form-data="formData" @click-field="click($event)"></product-geo-form>
                </div>
                <template v-if="formData.gln_of_information_provider.type!=='hidden'">
                    <div class="col-9">
                        <field-with-errors
                                :errors="formData.gln_of_information_provider.errors"
                                v-model="formData.gln_of_information_provider.value"
                                :label="formData.gln_of_information_provider.title"
                                :name="'gln_of_information_provider'"
                                :required="formData.gln_of_information_provider.required"
                                :valuetype="formData.gln_of_information_provider.type"
                                :description="formData.gln_of_information_provider.description"
                                :readonly="isGlnAutoFill ||formData.gln_of_information_provider.readonly"
                                @click.native="click(formData.gln_of_information_provider)"
                        ></field-with-errors>
                    </div>
                    <div class="col-3" style="padding-top: 32px;padding-left: 5px">
                        <label><input type='checkbox' id='gln-auto-fill' v-model="isGlnAutoFill"
                                      :readonly="formData.gln_of_information_provider.readonly"/>
                            {{ gettext('Default GLN') }}
                        </label>
                    </div>
                </template>
            </div>
        </template>
    </form-accordion>


</template>

<script>
    import FieldWithErrors from './FieldWithErrors';
    import FormAccordion from './FormAccordion';
    import ProductGeoForm from './ProductGeoForm';

    export default {
        name: "ProductOtherForm",
        components: {
            FieldWithErrors,
            FormAccordion,
            ProductGeoForm
        },
        props: {
            formData: {
                required: true
            },
            glnValue: {
                required: false,
                default: null
            },
            serverErrors: {
                required: false,
                default: null
            }
        },
        data() {
            return {
                isGlnAutoFill: true,
                visible: false,
                defaultGln: '',
                formField: [
                    'country_of_origin',
                    'target_market',
                    'language',
                    'gln_of_information_provider'
                ]
            }
        },
        computed: {
            isGeoBlockShowed() {
                return this.formField.some((key) => {
                    return this.formData[key].type !== 'hidden'
                })
            }
        },
        methods: {
            click(form) {
                this.$emit('click-field', form)
            },
            gettext(text) {
                return gettext(text)
            }
        },
        watch: {
            isGlnAutoFill(newVal) {
                if (newVal) {
                    this.formData.gln_of_information_provider.value = this.defaultGln;
                }
            },
            serverErrors(val) {
                if (val) {
                    this.visible = this.visible || this.formField.some((key) => {
                        return val[key];
                    })
                }
            },
        },
        mounted() {
            this.defaultGln = this.glnValue || this.formData.gln_of_information_provider.value;
            this.isGlnAutoFill = this.formData.gln_of_information_provider.value === this.glnValue;
        },
    }
</script>

<style scoped>

</style>
