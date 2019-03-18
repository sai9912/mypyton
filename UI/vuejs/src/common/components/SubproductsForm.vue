<template>
    <form-accordion :visible="visibleModel" v-if="packageLevel!==70">
        <template slot="header">
            <span>{{ gettext('Subproducts') }}</span>
        </template>
        <template slot="body">
            <div class="well">
                <table id="subproducts_tbl"
                       class="table table-sm"
                       style="width:100%"
                       :items="subproduct_items">
                    <thead>
                    <tr>
                        <th>{{ gettext('GTIN') }}</th>
                        <th>{{ gettext('Package level') }}</th>
                        <th>{{ gettext('Product description') }}</th>
                        <th>{{ gettext('Quantity') }}</th>
                        <th></th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="product,i in subproducts">
                        <td>{{ product.gtin.value }}</td>
                        <td style="text-align:center">{{ product.package_level.value }}</td>
                        <td style="text-align:center">{{ getvalue(product.description_i18n.value) }}</td>
                        <td style="text-align:center"><input v-model="product.count"
                                                             @change="verify_count(product.count, i)"
                                                             style="border:none"></td>
                        <td style="color:red; cursor:pointer"
                            @click="remove_subproduct(i)">
                            <span class="remove-icon">×</span>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </template>
    </form-accordion>
</template>

<script>
    import FieldWithErrors from './FieldWithErrors';
    import FormAccordion from './FormAccordion';
    import APIService from '../../common/services/APIService';
    import _ from 'lodash';

    export default {
        components: {
            FieldWithErrors,
            FormAccordion
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
        computed: {
            gtin: {
                get() {
                    return this.$store.state.ProductCreation.gtin;
                },
            }
        },
        data() {
            return {
                visibleModel: this.visible,
                subproducts: [],
                count: 2
            };
        },
        methods: {
            gettext(text) {
                return text;
            },
            getvalue(text) {
                return _.values(text)[0];
            },
            verify_count(count, i) {
                if (count < 0) {
                    this.subproducts[i].count = -count;
                } else {
                    // this.subproducts[i].count = count;
                }
                this.$store.commit('ProductCreation/setSubproducts', this.subproducts);
            },
            remove_subproduct(i) {
                console.log(i)
                this.subproducts.splice(i, 1)
                this.$store.commit('ProductCreation/setSubproducts', this.subproducts);
            },
            get_locale_value(obj, lang) {
                let ret = ''
                try {
                    ret = obj.value[lang]
                } catch (e) {
                    try {
                        ret = obj.value['en']
                    } catch (e) {
                    }
                }
                return ret
            }
        },
        watch: {
            serverErrors(val) {
                if (val) {
                    this.visibleModel = this.visibleModel || val.image_i18n
                }
            }
        },
        mounted() {
            APIService.getSubproducts('create').then(subproducts => {
                this.subproducts = subproducts;
                this.$store.commit('ProductCreation/setSubproducts', this.subproducts);
                if (subproducts) {
                    let lang = 'en'
                    for (let l in this.formData.language.enum) {
                        if (this.formData.language.enum[l][0] == this.formData.language.value) {
                            lang = this.formData.language.enum[l][2]
                        }
                    }
                    // this.formData.description_i18n.value = this.get_locale_value(subproducts[0].description_i18n, lang)
                    this.formData.brand_i18n.value = this.get_locale_value(subproducts[0].brand_i18n, lang)
                    this.formData.sub_brand.value = this.get_locale_value(subproducts[0].sub_brand, lang)
                    this.formData.functional_name_i18n.value = this.get_locale_value(subproducts[0].functional_name_i18n, lang)
                    this.formData.variant.value = this.get_locale_value(subproducts[0].variant, lang)
                    this.formData.category.value = this.get_locale_value(subproducts[0].category, lang)
                }
            });
        }
    }
</script>

<style lang="scss">
    .thumbnail {
        margin: 10px 0;
        img {
            max-height: 300px;
            max-width: 300px;
        }
    }

    .image-error {
        margin-bottom: 10px;
        font-size: 11px;
    }

    .well.well-sm {
        padding: 5px 0;
    }

    .image_clear {
        margin-bottom: 10px;
    }

    .remove-icon {
        font-size: 22px;
    }
</style>
