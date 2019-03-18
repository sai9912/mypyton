<template>
    <div class="product-list">

        <div v-if="!loadingPage">
            <div class="list-header">
                <h3>{{ gettext('Edit your product catalogue') }}


                </h3>

                <template v-if="userData.product_active_prefix.prefix.is_special !== 'READ-ONLY'">
                    <router-link
                            to="products/add"
                            class="btn btn-primary float-right"
                            v-if="isSpa">
                        {{ gettext('Add product') }}
                    </router-link>
                    <a href="/products/js-add" class="btn btn-primary float-right"
                       v-else>{{ gettext('Add product') }}</a>
                </template>

                <a class="btn btn-gs1ie-orange pull-right" href="/products/add?express=1" v-if="false"
                   style="margin-right:10px;">'Express Allocation'</a>
            </div>


            <list-filter :current-filter="currentFilter"
                         :order="order"
                         :is-open="isOpenFilters"
                         :user-data="userData"
                         @apply="applyFilter($event)"></list-filter>
            <div class="table-block">
                <div class="table-container">

                    <table class="table table-striped">


                        <thead>
                        <th></th>
                        <th>&nbsp;</th>


                        <sort-indicator :order="order" order-key="package_level" @change="changeSort($event)">
                            {{ gettext('Package Level') }}
                        </sort-indicator>


                        <sort-indicator :order="order" order-key="brand_i18n" @change="changeSort($event)">
                            {{ gettext('Brand') }}
                        </sort-indicator>


                        <sort-indicator :order="order" order-key="description_i18n" @change="changeSort($event)">
                            {{ gettext('Description') }}
                        </sort-indicator>


                        <sort-indicator :order="order" order-key="sku" @change="changeSort($event)"
                                        v-if="userData.member_organisation!=='gs1se'">
                            {{ gettext('SKU') }}
                        </sort-indicator>


                        <sort-indicator :order="order" order-key="gtin" @change="changeSort($event)">
                            {{ gettext('GTIN') }}
                        </sort-indicator>

                        <th style="text-align: center">{{ gettext('Barcode') }}</th>
                        <th style="text-align: center">{{ gettext('GS1 Cloud') }}</th>
                        </thead>
                        <tbody>

                        <template>
                            <template v-for="item in items" >
                                <tr :key="item.id">
                                    <td>
                                        <star-control :value="item.mark"
                                                      :gtin="item.gtin"
                                                      @input="changeFavorite(item, $event)"></star-control>
                                    </td>
                                    <td>
                                    <span v-if="item.products.length>0" class="control-sub-product accent-link"
                                          @click="item.showSubProduct = !item.showSubProduct">


                                        <i class="fas fa-chevron-down" v-if="!item.showSubProduct"></i>
                                        <i class="fas fa-chevron-up" v-if="item.showSubProduct"></i>
                                    </span>

                                    </td>
                                    <td style="vertical-align:middle; text-align:center;">
                                        <package-level-indicator
                                                :package-level="item.package_level"></package-level-indicator>
                                    </td>
                                    <td>
                                        {{item.brand_i18n}}
                                    </td>
                                    <td>
                                        <a :href="'/products/' + item.id+ '/fulledit_js'" class="accent-link">
                                            {{item.description_i18n}}
                                        </a>
                                    </td>
                                    <td v-if="userData.member_organisation!=='gs1se'">
                                        {{item.sku}}
                                    </td>
                                    <td style="white-space:nowrap;color:#002C6C;text-align:right;">
                                        {{item.gtin}}
                                    </td>
                                    <td style="text-align: center">
                                        <a :href="'/products/' + item.id+ '/fulledit_js#symbols'" class="accent-link">
                                            <i class="fas fa-barcode"></i>
                                        </a>
                                    </td>
                                    <td style="text-align: center">
                                        <a :href="'/products/' + item.id+ '/fulledit_js'" class="accent-link" v-if="item.package_level===70">
                                            <i class="material-icons cloud-icon" v-if="item.gs1_cloud_state ==='ACTIVE'">
                                                cloud
                                            </i>
                                            <i class="material-icons cloud-icon cloud-icon--disabled " v-else>
                                                cloud_queue
                                            </i>
                                        </a>
                                    </td>
                                </tr>
                                <template v-if="item.products.length>0 && item.showSubProduct">
                                    <tr v-for="subProduct in item.products" class="sub-product-row">
                                        <td class="table-warning">

                                        </td>
                                        <td class="table-warning">


                                        </td>
                                        <td style="vertical-align:middle; text-align:center;" class="table-warning">
                                            <package-level-indicator
                                                    :package-level="subProduct.package_level"></package-level-indicator>
                                        </td>
                                        <td class="table-warning">
                                            {{subProduct.brand_i18n}}
                                        </td>
                                        <td class="table-warning">
                                            <a href="" class="accent-link">
                                                {{subProduct.description_i18n}}
                                            </a>
                                        </td>
                                        <td class="table-warning" v-if="userData.member_organisation!=='gs1se'">
                                            {{subProduct.sku}}
                                        </td>
                                        <td style="white-space:nowrap;color:#002C6C;text-align:right;"
                                            class="table-warning">
                                            {{subProduct.gtin}}
                                        </td>
                                        <td style="text-align: center" class="table-warning">
                                            {{subProduct.quantity}}
                                        </td>
                                        <td style="text-align: center">

                                        </td>
                                    </tr>
                                </template>


                            </template>
                        </template>


                        </tbody>
                    </table>


                    <div v-if="items.length ===0 && !loading && !currentFilter">
                        {{gettext("No products found, please")}}
                        <span>
                             <router-link
                                     to="products/add"
                                     class="btn btn-primary float-right"
                                     v-if="isSpa">
                        {{ gettext('add product') }}
                    </router-link>
                    <a href="/products/js-add"
                       v-else>{{ gettext('add product') }}</a>
                        </span>.

                    </div>
                    <div v-if="items.length ===0  && !loading && currentFilter">
                        {{gettext(" No products found, please change or reset filters.")}}
                    </div>

                    <div>
                        <div class="table-backdrop" v-if="loading">
                        </div>
                        <spinner-indicator class="spinner-block" :loading="loading"></spinner-indicator>
                    </div>
                </div>


                <div class="mt-3 paginator">

                    <div class="pagination">
                        <b-pagination
                                size="md"
                                :total-rows="totalRows"
                                v-model="currentPage"
                                :per-page="perPage"
                                :hide-goto-end-buttons="true"
                                :prev-text="gettext('Previous')"
                                :next-text="gettext('Next')"
                        >
                        </b-pagination>
                    </div>
                    <div class="total-items">
                        <span v-if="false">{{ gettext('Total') }} - 68</span>
                    </div>
                    <div class="per-page">
                        <div class="per-page-label">{{ gettext('Products per page') }}:</div>
                        <b-form-select class="per-page-select" v-model="perPage" :options="options"/>
                    </div>
                </div>
            </div>

        </div>

        <spinner-indicator class="spinner-block" :loading="loadingPage"></spinner-indicator>


    </div>


</template>

<script>
    import ProductsService from '../../common/services/ProductsService'
    import SpinnerIndicator from "../../common/components/SpinnerIndicator";
    import PackageLevelIndicator from '../PackageLevelIndicator/PackageLevelIndicator'
    import StarControl from '../StarControl/StarControl'
    import SortIndicator from '../SortIndicator/SortIndicator'
    import ListFilter from './ListFilter'
    import * as _ from 'lodash'
    import APIService from "../../common/services/APIService";

    const filterVersion = '0.1'
    export default {
        name: 'list-products',
        components: {
            PackageLevelIndicator,
            ListFilter,
            StarControl,
            SpinnerIndicator,
            SortIndicator
        },
        props: {
            activePrefixGtin: {
                required: false,
                default: '1'
            },
            prefixIsReadOnly: {
                required: false,
                default: false
            },
            isSpa: {
                required: false,
                default: false
            },
            userDataOuter: {
                required: false
            }
        },
        data() {
            return {
                items: [],
                empty: false,
                loading: true,
                currentPage: 1,
                perPage: 10,
                totalRows: 0,
                order: {
                    key: 'gtin',
                    isDesc: true
                },
                options: [
                    {value: 10, text: '10'},
                    {value: 20, text: '20'},
                    {value: 50, text: '50'}
                ],
                isOpenFilters: false,
                currentFilter: null,
                loadingPage: true,
                userData: null
            }
        },
        computed: {
            /*activePrefixGtin() {
                return this.$store.state.prefixes.activePrefixId
            },
            prefixIsReadOnly() {
                return this.$store.state.prefixes.activePrefix && this.$store.state.prefixes.activePrefix.is_special === 'READ-ONLY'
            }*/
        },
        watch: {
            perPage(val) {
                this.loadProducts()
            },
            currentPage(val) {
                this.loadProducts()
            },
            activePrefixGtin(value) {
                if (value) {
                    this.loadProducts(value)
                }
            }
        },
        methods: {
            gettext(val) {
                return gettext(val);
            },
            applyFilter({filter, order}) {
                this.order = order
                this.currentFilter = filter
                this.loadProducts()
            },
            changeFavorite(product, val) {
                product.mark = val
            },
            transformProduct(product) {
                return Object.keys(product).reduce((res, key) => {
                    if (product[key].value !== undefined) {
                        if (_.endsWith(key, '_i18n')) {
                            res[key] = product[key].value && product[key].value[Object.keys(product[key].value)[0]]
                        } else {
                            res[key] = product[key].value
                        }
                        return res
                    } else {
                        res[key] = product[key]
                        return res
                    }

                }, {})
            },
            changeSort(sort) {
                this.order = sort;
                this.loadProducts()
            },
            loadProducts(prefix) {
                this.loading = true


                let params = {
                    page: this.currentPage,
                    products_per_page: this.perPage,
                    order: this.order.key,
                    is_desc: this.order.isDesc,
                    prefix: this.userData.product_active_prefix.prefix
                }
                if (this.currentFilter) {
                    const filter = this.currentFilter
                    params = Object.assign(params, {
                        base: filter.base ? 1 : 0,
                        pack: filter.pack ? 1 : 0,
                        case: filter.case ? 1 : 0,
                        pallet: filter.pallet ? 1 : 0,
                        display_shipper: filter.display_shipper ? 1 : 0,
                        mark: filter.mark ? 'on' : '',
                        brand: this.currentFilter.brand,
                        gtin: this.currentFilter.gtin,
                        description: this.currentFilter.description,
                        sku: this.currentFilter.sku,
                        target_market: this.currentFilter.target_market && this.currentFilter.target_market.code,
                        search: this.currentFilter.search
                    })
                }
                this.saveParams()
                ProductsService.getList(params)
                    .then((result) => {
                        this.items = result.products.map((obj) => {
                            const product = this.transformProduct(obj);
                            if (product.products && product.products.length > 0) {
                                product.products = product.products.map((sub) => {
                                    const subProduct = this.transformProduct(sub.sub_product)
                                    subProduct.quantity = sub.quantity
                                    return subProduct
                                })
                            }
                            product.showSubProduct = false
                            return product

                        })
                        this.totalRows = result.pagination_numpages * this.perPage
                    })
                    .finally(() => {
                        this.loading = false
                    })
            },
            loadUserData() {
                return this.$http.get(`/api/v1/accounts/info/`).then(response => {
                    this.userData = response.data.user;
                });
            },
            restoreParams() {
                const params = JSON.parse(this.$localStorage.get('productsParams'))
                if (params && params.userId === this.userData.id && filterVersion === params.version) {
                    this.currentFilter = params.filter;
                    this.isOpenFilters = !!this.currentFilter;
                    this.order = params.order;
                }
            },
            saveParams() {
                const params = {
                    filter: this.currentFilter,
                    order: this.order,
                    userId: this.userData.id,
                    version: filterVersion
                }
                this.$localStorage.set('productsParams', JSON.stringify(params))
            },
            init() {
                this.restoreParams()
                this.loadProducts()
            }
        },
        mounted() {
            this.loadingPage = true;
            if (this.userDataOuter) {
                this.userData = this.userDataOuter;
                this.loadingPage = false;
                this.init()
            } else {
                this.loadUserData().then(() => {
                    this.init()
                }).finally(() => {
                    this.loadingPage = false;
                });
            }
        }
    }
</script>

<style scoped lang="scss">
    .paginator {
        display: flex;
        justify-content: space-between;
        align-items: center;

    }

    .pagination {
        margin-bottom: 0rem;
    }

    .list-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
    }

    .fas.fa-barcode {
        font-size: 18px;
    }

    .filters {
        .card {
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-top: none;
        }

    }

    .per-page {
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    .per-page-label {
        padding-right: 0.5rem;
    }

    .per-page-select {
        width: 70px;
    }

    .table-block {
        position: relative;
    }

    .table-container {
        min-height: 200px;
    }

    .spinner-block {
        padding: 3rem;
        position: absolute;
        top: calc(50% - 68px);
    }

    .table-backdrop {
        opacity: 0.2;
        background-color: #acacac;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        position: absolute;
        z-index: 1;
        transition: opacity .15s linear;
    }

    .control-sub-product {
        cursor: pointer;
        font-size: 16px;
    }

    .sub-product-row {

    }

    .accent-link {
        color: #f26334;
        &:hover {
            color: #bb4e2a;
        }
    }
    .cloud-icon
    {
        font-size: 18px;
    }
    .cloud-icon--disabled
    {
        color: #888b8d;
    }

</style>

<style lang="scss">

    .product-list {
        .page-item.active .page-link {
            background-color: #002c6c;
            border-color: #002c6c;
        }

        .page-link {
            color: #002c6c;
        }
    }


</style>
