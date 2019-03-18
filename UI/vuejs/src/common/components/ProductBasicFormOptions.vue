<template>
    <div>

        <form-accordion :visible="true" v-if="isOptionsShowed || formData.is_bunit.type!=='hidden'" class="mb-3">
            <template slot="header">
                <span>{{ gettext('Unit qualifiers') }}</span>
            </template>
            <template slot="body">

                <div class="row">
                    <div class="col-6" v-if="isOptionsShowed">

                        <div class="card">
                            <div class="card-header option-header">

                                {{ gettext('Mandatory') }}
                                <span class="option-header-note">{{ gettext('(Select One)') }}&nbsp;</span>

                            </div>
                            <div class="card-body">
                                <field-with-errors
                                        :errors="formData.is_cunit.errors"
                                        v-model="formData.is_cunit.value"
                                        :label="formData.is_cunit.title"
                                        :name="'is_cunit'"
                                        :required="formData.is_cunit.required"
                                        :valuetype="formData.is_cunit.type"
                                        :description="formData.is_cunit.description"
                                        :readonly="formData.is_cunit.readonly"
                                        @click.native="click(formData.is_cunit)"
                                ></field-with-errors>
                                <field-with-errors
                                        :errors="formData.is_dunit.errors"
                                        v-model="formData.is_dunit.value"
                                        :label="formData.is_dunit.title"
                                        :name="'is_dunit'"
                                        :required="formData.is_dunit.required"
                                        :valuetype="formData.is_dunit.type"
                                        :description="formData.is_dunit.description"
                                        :readonly="formData.is_dunit.readonly"
                                        @click.native="click(formData.is_dunit)"
                                ></field-with-errors>
                                <field-with-errors
                                        :errors="formData.is_vunit.errors"
                                        v-model="formData.is_vunit.value"
                                        :label="formData.is_vunit.title"
                                        :name="'is_vunit'"
                                        :required="formData.is_vunit.required"
                                        :valuetype="formData.is_vunit.type"
                                        :description="formData.is_vunit.description"
                                        :readonly="formData.is_vunit.readonly"
                                        @click.native="click(formData.is_vunit)"
                                ></field-with-errors>
                                <field-with-errors
                                        :errors="formData.is_iunit.errors"
                                        v-model="formData.is_iunit.value"
                                        :label="formData.is_iunit.title"
                                        :name="'is_iunit'"
                                        :required="formData.is_iunit.required"
                                        :valuetype="formData.is_iunit.type"
                                        :description="formData.is_iunit.description"
                                        :readonly="formData.is_iunit.readonly"
                                        @click.native="click(formData.is_iunit)"
                                ></field-with-errors>
                                <field-with-errors
                                        :errors="formData.is_ounit.errors"
                                        v-model="formData.is_ounit.value"
                                        :label="formData.is_ounit.title"
                                        :name="'is_ounit'"
                                        :required="formData.is_ounit.required"
                                        :valuetype="formData.is_ounit.type"
                                        :description="formData.is_ounit.description"
                                        :readonly="formData.is_ounit.readonly"
                                        @click.native="click(formData.is_ounit)"
                                ></field-with-errors>
                                <span class="help-block" style="color:red"
                                      v-if="optionalFieldsError"><p>{{ gettext('Options: At least one option must be selected.') }}</p></span>
                            </div>

                        </div>


                    </div>
                    <div class="col-6" v-if="formData.is_bunit.type!=='hidden'">

                        <div class="card">

                            <div class="card-header option-header">
                                {{ gettext('Optional') }}
                            </div>
                            <div class="card-body">
                                <field-with-errors
                                        :errors="formData.is_bunit.errors"
                                        v-model="formData.is_bunit.value"
                                        :label="formData.is_bunit.title"
                                        :name="'is_bunit'"
                                        :required="formData.is_bunit.required"
                                        :valuetype="formData.is_bunit.type"
                                        :description="formData.is_bunit.description"
                                        :readonly="formData.is_bunit.readonly"
                                        @click.native="click(formData.is_bunit)"
                                ></field-with-errors>
                            </div>
                        </div>

                    </div>
                </div>


            </template>
        </form-accordion>


    </div>
</template>

<script>
    import FieldWithErrors from './FieldWithErrors';
    import FormAccordion from './FormAccordion';

    export default {
        components: {
            FieldWithErrors,
            FormAccordion
        },
        props: {
            formData: {
                required: true
            },
        },
        methods: {
            click(form) {
                this.$emit('click-field', form)
            },
            gettext(text) {
                return gettext(text);
            },
        },
        computed: {
            optionalFieldsError() {
                let noError = ['is_cunit', 'is_dunit', 'is_vunit', 'is_iunit', 'is_ounit'].find(fieldName => {
                    if (this.formData[fieldName].value) {
                        return true;
                    }
                });
                if (noError) {
                    return false;
                }
                return true;
            },
            isOptionsShowed() {
                return [
                    this.formData.is_cunit.type,
                    this.formData.is_dunit.type,
                    this.formData.is_vunit.type,
                    this.formData.is_iunit.type,
                    this.formData.is_ounit.type
                ].some(type => type !== 'hidden')
            }
        }
    }
</script>

<style scoped>
    .option-header {
        font-size: 1rem;
    }

    .option-header-note {
        font-size: 0.8rem;
        vertical-align: center;
    }
</style>

