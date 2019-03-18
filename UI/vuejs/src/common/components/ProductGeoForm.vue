<template>
    <div class="row">
        <field-with-errors
                class="col-6"
                :errors="formData.country_of_origin.errors"
                v-model="formData.country_of_origin.value"
                :label="formData.country_of_origin.title"
                :name="'country_of_origin'"
                :required="formData.country_of_origin.required"
                :valuetype="formData.country_of_origin.type"
                :choices="formData.country_of_origin.enum"
                :description="formData.country_of_origin.description"
                :readonly="formData.country_of_origin.readonly"
                @click.native="click(formData.country_of_origin)"
        ></field-with-errors>
        <field-with-errors
                class="col-6"
                :errors="formData.target_market.errors"
                v-model="formData.target_market.value"
                :label="formData.target_market.title"
                :name="'target_market'"
                :required="formData.target_market.required"
                :valuetype="formData.target_market.type"
                :choices="formData.target_market.enum"
                :description="formData.target_market.description"
                :readonly="formData.target_market.readonly"
                @click.native="click(formData.target_market)"
        ></field-with-errors>
        <field-with-errors
                class="col-6"
                :errors="formData.language.errors"
                v-model="formData.language.value"
                :label="formData.language.title"
                :name="'language'"
                :required="formData.language.required"
                :valuetype="formData.language.type"
                :choices="formData.language.enum"
                :description="formData.language.description"
                :readonly="formData.language.readonly"
                @click.native="click(formData.language)"
        ></field-with-errors>
    </div>
</template>

<script>
    import FieldWithErrors from './FieldWithErrors';

    export default {
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
        components: {
            FieldWithErrors,
        }
    }
</script>
