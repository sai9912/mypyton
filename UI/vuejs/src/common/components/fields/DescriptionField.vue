<template>
    <div class="row" v-if="formData.description_i18n.type !== 'hidden'">
                <div class="col-9">
            <field-with-errors
                :errors="formData.description_i18n.errors"
                v-model="description"
                :label="formData.description_i18n.title"
                :name="'description_i18n'"
                :required="formData.description_i18n.required"
                :valuetype="formData.description_i18n.type"
                :description="formData.description_i18n.description"
                :readonly="formData.description_i18n.readonly"
                @click.native="click(formData.description_i18n)"
                :languages="languages"
                :language="language"
            ></field-with-errors>
        </div>
        <div class="col-3" style="padding-top: 32px;padding-left: 5px">
            <label><input type='checkbox' id='auto-fill' v-model="isAutoFill"/> Auto-Fill</label>
        </div>
    </div>
</template>

<script>
    import FieldWithErrors from '../FieldWithErrors';

    export default {
        name: "desctiptionField",
        components: {
            FieldWithErrors
        },
        props: {
            formData: {
                required: true
            },
            languages: {
                required: true
            },
            language: {
                required: true
            }
        },
        data() {
            return {
                isAutoFill: false
            }
        },
        computed: {
            description:
                {
                    get() {
                        if (this.isAutoFill) {
                            this.formData.description_i18n.value[this.language] = this.formData.brand_i18n.value[this.language] + ' ' + this.formData.functional_name_i18n.value[this.language];
                        }
                        return this.formData.description_i18n.value
                    },
                    set(val) {
                        this.isAutoFill = false
                        this.formData.description_i18n.value = val
                    }
                }
        },
        methods:{
            click(form) {
                this.$emit('click-field', form)
            }
        }
    }
</script>

<style scoped>

</style>
