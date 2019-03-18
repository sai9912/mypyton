<template>
    <div class="row">
        <div class='col-9 hide-empty'>
            <field-with-errors
                    :errors="formData.company.errors"
                    v-model="formData.company.value"
                    :label="formData.company.title"
                    :name="'company'"
                    :required="formData.company.required"
                    :valuetype="formData.company.type"
                    :description="formData.company.description"
                    :readonly="formData.company.readonly"
                    @click.native="click(formData.company)"
            ></field-with-errors>
        </div>


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
                    :languages="languages"
                    :language="language"
            >
            </field-with-errors>
        </div>

        <input
                type="hidden" name="label_description" id="label_description" v-else
                :value="formData.label_description_i18n.value"
        />
        <input type="hidden" name="mark" id="mark" :value="formData.mark.value" v-if="formData.mark"/>
        <!-- brand row -->

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
                    :languages="languages"
                    :language="language"
            ></field-with-errors>
        </div>
        <div class='col-6 hide-empty'>
            <field-with-errors
                    :errors="formData.sub_brand.errors"
                    v-model="formData.sub_brand.value"
                    :label="formData.sub_brand.title"
                    :name="'sub_brand'"
                    :required="formData.sub_brand.required"
                    :valuetype="formData.sub_brand.type"
                    :description="formData.sub_brand.description"
                    :readonly="formData.sub_brand.readonly"
                    @click.native="click(formData.sub_brand)"
            ></field-with-errors>
        </div>

        <!-- name / variant -->

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
                    :languages="languages"
                    :language="language"
            ></field-with-errors>
        </div>
        <div class='col-6 hide-empty'>
            <field-with-errors
                    :errors="formData.variant.errors"
                    v-model="formData.variant.value"
                    :label="formData.variant.title"
                    :name="'variant'"
                    :required="formData.variant.required"
                    :valuetype="formData.variant.type"
                    :description="formData.variant.description"
                    :readonly="formData.variant.readonly"
                    @click.native="click(formData.variant)"
            ></field-with-errors>
        </div>

        <div class='col-6 hide-empty'>
            <field-with-errors
                    :errors="formData.sku.errors"
                    v-model="formData.sku.value"
                    :label="formData.sku.title"
                    :name="'sku'"
                    :required="formData.sku.required"
                    :valuetype="formData.sku.type"
                    :description="formData.sku.description"
                    :readonly="formData.sku.readonly"
                    @click.native="click(formData.sku)"
            ></field-with-errors>
        </div>

        <!-- product-trade-item description row -->


        <description-field class="col-12" :form-data="formData" :languages="languages" :language="language" @click-field="click($event)"/>
        <!-- product-trade-item website_url row -->
        <template v-if="formData.website_url.type !== 'hidden'">
            <div class="col-9" style="padding-right: 3px">
                <field-with-errors
                        :errors="formData.website_url.errors"
                        v-model="formData.website_url.value"
                        :label="formData.website_url.title"
                        :name="'website_url'"
                        :required="formData.website_url.required"
                        :valuetype="formData.website_url.type"
                        :description="formData.website_url.description"
                        :readonly="formData.website_url.readonly"
                        @click.native="click(formData.website_url)"
                >
                </field-with-errors>
            </div>
        </template>

        <!-- product-trade-item point_of_sale row -->
        <template v-if="formData.point_of_sale.type !== 'hidden'">
            <div class="col-9" style="padding-right: 3px">
                <field-with-errors
                        :errors="formData.point_of_sale.errors"
                        v-model="formData.point_of_sale.value"
                        :label="formData.point_of_sale.title"
                        :name="'point_of_sale'"
                        :required="formData.point_of_sale.required"
                        :valuetype="formData.point_of_sale.type"
                        :description="formData.point_of_sale.description"
                        :readonly="formData.point_of_sale.readonly"
                        @click.native="click(formData.point_of_sale)"
                ></field-with-errors>
            </div>
        </template>
        <div class='col-12 gpc-select-block' v-if="formData.category.type!=='hidden'">
            <gpc-select v-model="formData.category.selectedObject"
                        @select="formData.category.value = $event"
                        :errors="formData.category.errors"
                        :required="formData.category.required"
                        :readonly="formData.category.readonly"
                        :gpc-loading="formData.category.loading"
                        :description="formData.category.description"
                        @click.native="click(formData.category)"
            >
            </gpc-select>
        </div>


    </div>
</template>

<script>
    import FieldWithErrors from './FieldWithErrors';
    import DescriptionField from './fields/DescriptionField';
    import GpcSelect from './GpcSelect';

    export default {
        data() {
            return {};
        },

        methods: {
            click(form) {
                this.$emit('click-field', form)
            },
            gettext(text) {
                return gettext(text);
            },
        },
        props: {
            formData: {
                required: true
            },
            packageLevelId: {
                required: true
            },
            languages: {
                required: true
            },
            language: {
                required: true
            }
        },
        watch: {},
        components: {
            FieldWithErrors,
            DescriptionField,
            GpcSelect
        }
    }
</script>

<style>
    .gpc-select-block {
        margin-bottom: 0.5rem;
    }
</style>
