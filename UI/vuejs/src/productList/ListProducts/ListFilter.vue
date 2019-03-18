<template>

    <div class="list-filter">
        <div>
            <b-input-group>
                <b-form-input type="text" v-model="filter.search"></b-form-input>

                <b-input-group-append>
                    <b-btn variant="outline-secondary"
                           :pressed="!!currentFilter"
                           @click="showFilters=!showFilters">
                        {{gettext("Filters")}} <span v-if="!!currentFilter">( {{gettext('Applied')}} )</span>
                        <i class="fas fa-filter"></i>
                    </b-btn>
                    <b-btn variant="info" @click="apply()">{{gettext('Search')}} <i class="fas fa-search"></i></b-btn>
                </b-input-group-append>
            </b-input-group>
        </div>

        <div class="mb-3 filters">
            <b-collapse
                    role="tabpanel"
                    v-model="showFilters"
                    id="filters"

            >
                <b-card :title="gettext('Filters')">

                    <b-card-body>

                        <div class="row">
                            <div class="col-6">
                                <b-form-group
                                        :label="gettext('Target Market')">

                                    <v-select label="name"
                                              :filterable="true"
                                              :options="targetMarkets"
                                              v-model="filter.target_market"
                                              :loading="targetMarketsLoading"
                                    >
                                        <template slot="no-options">
                                            {{ gettext('Results not found') }}
                                        </template>
                                    </v-select>

                                </b-form-group>
                                <fieldset
                                        class="b-form-group form-group"
                                        v-if="packageLevels"
                                >
                                    <legend class="col-form-label pt-0 ">{{gettext("Filters")}}</legend>
                                    <div class="row">

                                        <div class="col-7">
                                            <div  v-if="packageLevels['70']">
                                                <div class="checkbox">
                                                    <b-form-checkbox
                                                            v-model="filter.base"
                                                            value="true">
                                                        <div class="checkbox-label">
                                                            <package-level-indicator :package-level="70"
                                                                                     class="checkbox-icon"></package-level-indicator>
                                                            {{ gettext('Base Unit') }}

                                                        </div>

                                                    </b-form-checkbox>

                                                </div>
                                            </div>
                                            <div v-if="packageLevels['60']">
                                                <div class="checkbox">
                                                    <b-form-checkbox
                                                            v-model="filter.pack"
                                                            value="true"
                                                    >
                                                        <div class="checkbox-label">
                                                            <package-level-indicator :package-level="60"
                                                                                     class="checkbox-icon"></package-level-indicator>
                                                            {{ gettext('Pack') }}

                                                        </div>

                                                    </b-form-checkbox>

                                                </div>
                                            </div>


                                            <div  v-if="packageLevels['50']">
                                                <div class="checkbox">
                                                    <b-form-checkbox
                                                            v-model="filter.case"
                                                            value="true"
                                                    >
                                                        <div class="checkbox-label">
                                                            <package-level-indicator :package-level="50"
                                                                                     class="checkbox-icon"></package-level-indicator>
                                                            {{ gettext('Case or mixed case') }}

                                                        </div>
                                                    </b-form-checkbox>

                                                </div>
                                            </div>
                                            <div  v-if="packageLevels['40']">
                                                <div class="checkbox">
                                                    <b-form-checkbox
                                                            v-model="filter.display_shipper"
                                                            value="true"
                                                    >
                                                        <div class="checkbox-label">
                                                            <package-level-indicator :package-level="40"
                                                                                     class="checkbox-icon"></package-level-indicator>
                                                            {{ gettext('Display unit') }}

                                                        </div>

                                                    </b-form-checkbox>
                                                </div>
                                            </div>
                                            <div  v-if="packageLevels['30']">
                                                <div class="checkbox">
                                                    <b-form-checkbox
                                                            v-model="filter.pallet"
                                                            value="true"
                                                    >
                                                        <div class="checkbox-label">
                                                            <package-level-indicator :package-level="30"
                                                                                     class="checkbox-icon"></package-level-indicator>
                                                            {{ gettext('Pallet') }}

                                                        </div>
                                                    </b-form-checkbox>
                                                </div>
                                            </div>
                                        </div>


                                        <div class="col-5">
                                            <div class="checkbox">
                                                <b-form-checkbox
                                                        v-model="filter.mark"
                                                        value="true"
                                                >
                                                    <div class="checkbox-label">
                                                        <star-control :value="true" :readonly="true"
                                                                      class="checkbox-icon"></star-control>
                                                        {{ gettext('Starred') }}

                                                    </div>
                                                </b-form-checkbox>

                                            </div>
                                        </div>
                                    </div>
                                </fieldset>


                            </div>
                            <div class="col-6">
                                <div class="row">


                                    <div class="col-6 form-group">

                                        <b-form-group
                                                :label="gettext('Brand')"
                                        >
                                            <b-form-input v-model.trim="filter.brand"></b-form-input>
                                        </b-form-group>


                                    </div>
                                    <div class="col-6 form-group">
                                        <b-form-group
                                                :label="gettext('GTIN')"
                                        >
                                            <b-form-input v-model.trim="filter.gtin"></b-form-input>
                                        </b-form-group>
                                    </div>
                                    <div class="col-6 form-group">
                                        <b-form-group
                                                :label="gettext('Description')"
                                        >
                                            <b-form-input v-model.trim="filter.description"></b-form-input>
                                        </b-form-group>
                                    </div>
                                    <div class="col-6 form-group" v-if="userData.member_organisation!=='gs1se'">
                                        <b-form-group
                                                :label="gettext('SKU')"
                                        >
                                            <b-form-input v-model.trim="filter.sku"></b-form-input>
                                        </b-form-group>
                                    </div>
                                </div>


                            </div>

                        </div>
                        <div class="row justify-content-between mt-4">
                            <div class="row col align-items-center">

                                <div class="col-auto sort-by-label">
                                    {{gettext("Sort by")}}:
                                </div>
                                <div class="col-auto">
                                    <b-form-select v-model="orderKey" :options="sorting"/>
                                </div>
                                <div class="col-auto">

                                    <b-form-select v-model="isDesc" :options="desc"/>
                                </div>


                            </div>
                            <div>
                                <b-button variant="secondary" @click="reset()">{{gettext("Reset")}}</b-button>
                                <b-button variant="primary" @click="apply()">{{gettext("Apply")}}</b-button>
                            </div>
                        </div>
                    </b-card-body>
                </b-card>


            </b-collapse>
        </div>
    </div>


</template>

<script>
    import PackageLevelIndicator from './../PackageLevelIndicator/PackageLevelIndicator'
    import StarControl from './../StarControl/StarControl'
    import vSelect from 'vue-select'
    import APIService from "../../common/services/APIService";

    const defaultFilter = {
        base: true,
        pack: true,
        case: true,
        pallet: true,
        display_shipper: true,
        mark: false,
        brand: '',
        gtin: '',
        description: '',
        sku: '',
        search: ''
    }
    export default {
        name: 'ListFilter',
        components: {
            PackageLevelIndicator,
            StarControl,
            vSelect
        },
        props: {
            order: {
                required: true
            },
            currentFilter: {
                required: true
            },
            isOpen: {
                required: false,
                default: false
            },
            userData: {
                required: true
            }
        },
        data() {
            return {
                filter: Object.assign({}, defaultFilter, this.currentFilter || {}),
                showFilters: this.isOpen,
                targetMarkets: [],
                targetMarketsLoading: false,
                orderKey: this.order.key,
                sorting: [
                    {value: "gtin", text: this.gettext("GTIN")},
                    {value: "sku", text: this.gettext("SKU")},
                    {value: "package_level", text: this.gettext("Package Level")},
                    {value: "brand_i18n", text: this.gettext("Brand")},
                    {value: "description_i18n", text: this.gettext("Description")},
                    {value: "created", text: this.gettext("Created")},
                    {value: "updated", text: this.gettext("Updated")}
                ],
                isDesc: this.order.isDesc,
                desc: [
                    {value: true, text: this.gettext("Descending")},
                    {value: false, text: this.gettext("Ascending")}
                ],
                packageLevels: null
            }
        },
        methods: {
            gettext(val) {
                return gettext(val);
            },
            apply() {
                this.$emit('apply', {
                    filter: this.filter,
                    order: {
                        key: this.orderKey,
                        isDesc: this.isDesc
                    }
                })
            },
            reset() {
                this.filter = Object.assign({}, defaultFilter)
                this.$emit('apply', {
                    filter: null,
                    order: {
                        key: 'gtin',
                        isDesc: true
                    }
                })
            }
        },
        mounted() {
            this.targetMarketsLoading = true;

            APIService.getPackagingLevels(this.userData.language, this.userData.member_organisation)
                .then((result) => {
                    this.packageLevels = result.reduce((result, item) => {
                        result[item.id] = true
                        return result;
                    }, {});
                    console.log(this.packageLevels)
                })
                .finally(() => {
                    this.targetMarketsLoading = false;
                })
            APIService.getTargetMarkets()
                .then((items) => {
                    this.targetMarkets = items;
                })
                .finally(() => {
                    this.targetMarketsLoading = false;
                })
        },
        watch: {
            order(val) {
                this.orderKey = val.key;
                this.isDesc = val.isDesc;
            },
            currentFilter(val) {
                if (val) {
                    this.filter = val;
                }
            }
        }
    }
</script>

<style scoped lang="scss">
    .checkbox-label {
        display: flex;
        align-items: baseline;
        margin-bottom: 6px;
    }

    .checkbox-icon {
        margin-right: 8px;
    }

    .card {
        background: white;
    }

    .sort-by-label {
        font-weight: 600;
    }


</style>

<style lang="scss">
    .list-filter {
        .col-form-label {
            font-weight: 600;
        }
    }
</style>
