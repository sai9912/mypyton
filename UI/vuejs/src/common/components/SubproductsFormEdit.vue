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
                        <td style="text-align:center">{{ product.package_level.ui_level }}</td>
                        <td style="text-align:center">{{ getvalue(product.description_i18n.value) }}</td>
                        <td style="text-align:center"><input v-model="product.quantity"
                                                             @change="verify_quantity(product.quantity, i)"
                                                             style="border:none"></td>
                        <td style="color:red; cursor:pointer;"
                            @click="remove_subproduct(i)">
                            <span class="remove-icon">×</span>
                        </td>
                    </tr>
                    </tbody>
                </table>
                <a class='btn btn-success' href="javascript:void(0)" data-toggle="modal"
                   data-target="#ProductAddSubs"
                   @click="add_subproducts()">{{ gettext('Add subproducts') }}
                </a>
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
                quantity: 2
            };
        },
        methods: {
            gettext(text) {
                return text;
            },
            getvalue(text) {
                return _.values(text)[0];
            },
            verify_quantity(quantity, i) {
                if (quantity < 0) {
                    this.subproducts[i].quantity = -quantity;
                } else {
                    // this.subproducts[i].quantity = quantity;
                }
                //this.$store.commit('ProductCreation/setSubproducts', this.subproducts);
                this.formData.subproducts = this.subproducts
            },
            remove_subproduct(i) {
                console.log(i)
                this.subproducts.splice(i, 1)
                this.formData.subproducts = this.subproducts
                //this.$store.commit('ProductCreation/setSubproducts', this.subproducts);
            },
            add_subproducts() {
                let gtin = this.formData.gtin.value
                let package_level = this.formData.package_level.value
                document.location.href = '/products/subproduct/add/case_edit/?gtin=' + gtin + '&package_level=' + package_level
            },
            load_subproducts() {
                let gtin = this.formData.gtin.value
                APIService.getSubproducts(gtin).then(subproducts => {
                    console.log(subproducts);
                    this.subproducts = subproducts
                    this.subproducts_orig = {}
                    for (let i in this.subproducts) {
                        let subproduct = this.subproducts[i]
                        this.subproducts_orig[subproduct.gtin.value] = subproduct.quantity
                    }
                    this.formData.subproducts = this.subproducts
                    // this.$store.commit('ProductCreation/setSubproducts', this.subproducts);
                })
            },
            find_subproduct(gtin) {
                for (let i in this.subproducts) {
                    let subproduct = this.subproducts[i]
                    if (subproduct.gtin.value == gtin) {
                        return subproduct.quantity
                    }
                }
                return 0
            },
            find_subproduct_orig(gtin) {
                let quantity = this.subproducts_orig[gtin]
                if (typeof(quantity) == 'undefined') {
                    return 0
                }
                return quantity
            },
            save_subproducts() {
                for (let i in this.subproducts) {
                    let subproduct = this.subproducts[i]
                    let quantity_orig = parseInt(this.find_subproduct_orig(subproduct.gtin.value))
                    let quantity = parseInt(subproduct.quantity)
                    if (quantity != quantity_orig) {
                        if (quantity_orig == 0) {
                            // add new subproduct
                            APIService.subproductCreate(this.formData.gtin.value, subproduct.gtin.value, subproduct.quantity)
                        } else {
                            // modify quantity
                            APIService.subproductEditQuantity(this.formData.gtin.value, subproduct.gtin.value, subproduct.quantity)
                        }
                    }
                }
                for (let subproduct in this.subproducts_orig) {
                    // delete 
                    // let quantity_orig = parseInt(this.subproducts_orig[subproduct])
                    let quantity = parseInt(this.find_subproduct(subproduct))
                    if (quantity == 0) {
                        APIService.subproductDelete(this.formData.gtin.value, subproduct)
                    }
                }
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
            this.load_subproducts()
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
