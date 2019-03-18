<template>
    <div>
        <div v-if="!isLoading">
            <!--
                   todo: check alerts
                   todo: check agreed flag
                   todo: check gln_capability
                   -->
            <!-- Prefix information and buttons start -->
            <b-alert show variant="danger" v-for="error in non_field_errors">
                {{ error }}
            </b-alert>

            <div class="row">
                <div class="col-md-4" v-if="memberOrganization.display_prefix_info">
                    <div id="active-prefix" class="well well-sm">
                        <h4>{{ gettext('Active Prefix') }}</h4>
                        <ul class="list-unstyled">
                            <li>{{ gettext('GCP') }}: <b>{{ product_active_prefix.prefix }}</b></li>
                            <li><b>{{ gettext('Products') }}:</b></li>
                            <li class="active-prefix-score">
                                {{ gettext('Allocated') }}: <b>{{ product_active_prefix.gtins_allocated }}</b>
                            </li>
                            <li class="active-prefix-score">
                                {{ gettext('Available') }}: <b>{{ product_active_prefix.gtins_available }}</b>
                            </li>

                            <!--
                            {% if user.company_organisations_companyorganisation.first.gln_capability %}
                                <li><b>{% trans 'Locations' %}:</b></li>
                                <li>&nbsp;&nbsp;&nbsp;&nbsp;{% trans 'Allocated' %}: <b>{{ range_data.3 }}</b></li>
                                <li>&nbsp;&nbsp;&nbsp;&nbsp;{% trans 'Available' %}: <b>{{ range_data.4 }}</b></li>
                            {% endif %}
                            -->
                        </ul>
                    </div>
                </div>
                <div class="col-md-8" :class="memberOrganization.display_prefix_info ? 'col-md-8':'col-md-12 row'">
                    <div :class="{'col-md-6': !memberOrganization.display_prefix_info}">
                        <a href="/products/js-add/" class="btn btn-primary">
                            {{ gettext('Add product') }}
                        </a>
                        <p style="margin-top: 10px;">{{ gettext('Allocate a new barcode from the Active Prefix') }}</p>
                    </div>
                    <div :class="{'col-md-6': !memberOrganization.display_prefix_info}">
                        <a href="/products/js-list" class="btn btn-gs1ie-orange">{{ gettext('View Products') }}</a>
                        <p style="margin-top: 10px;">{{ gettext('View allocated numbers from Active Prefix') }}</p>
                    </div>
                </div>
            </div>
            <!-- Prefix information and buttons finish -->

            <!-- Ranges table start -->
            <div class="row">
                <div class="col-md-12">
                    <div id="ranges-table" class="panel panel-primary">
                        <div class="panel-heading">
                            {{ gettext('Global Company Prefixes and GTIN Ranges') }}
                        </div>
                        <div class="panel-body">
                            <table class="table table-condensed table-striped">
                                <thead>
                                <tr>
                                    <th>
                                        &nbsp;
                                    </th>
                                    <th>
                                        {{ gettext('Prefix') }}
                                    </th>
                                    <th class="col-description">
                                        {{ gettext('Description') }}
                                    </th>
                                    <!--<th>
                                        {{ gettext('Starting from') }}
                                    </th>-->
                                    <th>
                                        {{ gettext('Products') }}
                                    </th>
                                    <th>
                                        {{ gettext('Capacity') }}
                                    </th>

                                </tr>
                                </thead>
                                <tbody>
                                <tr v-for="prefix in prefixes">
                                    <td class="prefix-star-col">
                                    <span class="prefix-star"
                                          :class="{'prefix-star-set': prefix.prefix === product_active_prefix.prefix}"
                                          @click="$refs.activatePrefixModal.open(prefix)">
                                    </span>
                                    </td>
                                    <td>
                                        {{ prefix.prefix }}
                                    </td>
                                    <td>
                                        <inline-text-edit-field
                                                v-model="prefix.description"
                                                :default_text="gettext('Block of __number__ GTINs').replace('__number__', prefix.gtins_capacity)"
                                                @ok="updatePrefixData(prefix)">
                                        </inline-text-edit-field>
                                    </td>
                                    <!--<td>-->
                                    <!--<span v-html="renderHighlightedGTIN(prefix.prefix, prefix.range[0])"></span>-->
                                    <!--<span v-html="renderHighlightedGTIN(prefix.prefix, prefix.range[1])"></span>-->
                                    <!--</td>-->
                                    <td>
                                        <!-- 1 product -->
                                        <template v-if="prefix.gtins_allocated === 1">
                                            <a :href="`/products/js-list?prefix=${prefix.prefix}`">1 {{ gettext('Product') }}</a>
                                        </template>
                                        <!-- 2+ products -->
                                        <template v-else-if="prefix.gtins_allocated > 1">
                                            <a :href="`/products/js-list?prefix=${prefix.prefix}`">
                                                {{ prefix.gtins_allocated }} {{ gettext('Products') }}
                                            </a>
                                        </template>
                                        <!-- no products -->
                                        <template v-else>
                                            <span class="text-muted">{{ gettext('No products') }}</span>
                                        </template>
                                    </td>
                                    <td>
                                        {{ prefix.gtins_available }}
                                    </td>
                                </tr>
                                </tbody>
                            </table>


                            <spinner-indicator :loading="isLoadingPrefix" class="prefix-spinner"></spinner-indicator>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Ranges table finish -->

            <!-- Account summary start -->
            <div class="row" v-if="memberOrganization.display_account_info">
                <div class="col-md-12">
                    <div class="panel panel-default account-summary">
                        <div class="panel-heading">
                            {{ gettext('Account Summary') }}
                        </div>
                        <div class="panel-body">
                            <template v-if="company_organisation.credit_points_balance">
                                <h4>{{ gettext('Symbol Credits') }}</h4>
                                <p>{{ gettext('Points balance:') }}<strong>{{ company_organisation.credit_points_balance
                                    }}</strong></p>
                            </template>

                            <!--
                            <p><a href="/profile/Apply-for-Licences/">{{ gettext('Purchase barcode image credits now') }}</a></p>
                            -->
                            <p>{{ gettext('Company ID:') }} {{ company_organisation.uuid }}</p>
                            <p>{{ gettext('Company Name:') }} {{ company_organisation.name }}</p>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Account summary finish -->

            <activate-prefix-modal @ok="setActivePrefix" ref="activatePrefixModal"></activate-prefix-modal>
        </div>
        <spinner-indicator :loading="isLoading" class="main-spinner"></spinner-indicator>
    </div>
</template>


<script>
    import APIService from '../../common/services/APIService';
    import ActivatePrefixModal from "./ActivatePrefixModal";
    import InlineTextEditField from "../../common/components/InlineTextEditField";
    import SpinnerIndicator from "../../common/components/SpinnerIndicator";

    import _ from 'lodash';
    import default_state from '../default_state';

    export default {
        props: {
            userData: {
                required: false
            },
            isSpa: {
                required: false
            }
        },
        data() {
            // if you don't see an expected variable,
            // check 'default_state.json', it must be specified there with an initial value
            return {
                ...default_state,
                isLoading: true,
                memberOrganization: false,
                isLoadingPrefix: false,
                prefixes: [],
                non_field_errors: []
            };
        },
        computed: {},
        watch: {},
        methods: {
            gettext(text) {
                return gettext(text);
            },
            setUserData(userData) {
                if (userData) {
                    _.forEach(this.user, (value, key) => {
                        let api_value = userData[key];
                        if (api_value !== undefined && !_.isObject()) {
                            this.user[key] = api_value;
                        }
                    });
                    if (userData.product_active_prefix) {
                        _.forEach(this.product_active_prefix, (value, key) => {
                            let api_value = userData.product_active_prefix[key];
                            if (api_value !== undefined) {
                                this.product_active_prefix[key] = api_value;
                            }
                        })
                    }

                }
            },
            loadUserData() {
                return this.$http.get(`/api/v1/accounts/login/`).then(response => {
                        this.setUserData(response.body.user);
                        return this.user;
                    },
                    response => {
                        this.handleAPIErrors(response);
                    });
            },
            loadCompanyOrganisation(co_slug) {
                APIService.getCompanyOrganisation(co_slug).then(
                    response => {
                        this.company_organisation = response
                    },
                    response => {
                        this.handleAPIErrors(response)
                    },
                );
            },
            loadMemberOrganization(co_slug) {
                if (this.user.company_organisation) {
                    return APIService
                        .getMemberOrganisation(co_slug)
                        .then(memberOrganization => {
                            this.memberOrganization = memberOrganization;
                            if (this.memberOrganization.display_account_info && this.user.company_organisation) {
                                this.loadCompanyOrganisation(this.user.company_organisation);
                            }
                        });
                }
            },
            loadPrefixesData() {
                this.isLoadingPrefix = true;
                this.prefixes = [];
                APIService.getPrefixes().then(
                    response => {
                        this.prefixes = response
                    },
                    response => {
                        this.handleAPIErrors(response)
                    },
                ).finally(() => {
                    this.isLoadingPrefix = false;
                });
            },
            handleAPIErrors(response) {
                if (typeof response.body === 'string') {
                    this.non_field_errors = ['Internal Error. Please contact Support.'];
                } else if (Array.isArray(response.body)) {
                    this.non_field_errors = response.body;
                }
                console.log('API Error:', response.body);
            },
            confirmActivePrefix(prefix) {
                this.$refs.activatePrefixModal.open(prefix);
            },
            setActivePrefix(prefix) {
                let patch_data = {
                    'product_active_prefix': prefix.prefix,
                };
                this.$http.patch(`/api/v1/users/${this.user.id}/update`, patch_data).then(
                    response => {
                        // if response is OK, reload user/prefixes data
                        _.forOwn(this.product_active_prefix, (value, key) => {
                            this.product_active_prefix[key] = null;
                        });

                        this.loadUserData();
                        this.loadPrefixesData();
                    },
                    response => {
                        this.handleAPIErrors(response)
                    },
                );
            },
            renderHighlightedGTIN(prefix, gtin) {
                let starting_from = gtin;
                if (_.startsWith(starting_from, '0')) {
                    starting_from = starting_from.slice(1);
                }
                let part1 = prefix;
                let part2 = starting_from.slice(part1.length, 12);
                let part3 = starting_from.slice(part1.length + part2.length);

                return `<span class="prefix-gtin">${part1}<span class="gtin-part-highlight">${part2}</span>${part3}</span>`;
            },
            updatePrefixData(prefix) {
                let patch_data = {description: prefix.description};

                this.$http.patch(`/api/v1/prefixes/${prefix.prefix}/`, patch_data).then(
                    response => {
                        // if response is OK, reload prefixes data
                        this.loadPrefixesData();
                    },
                    response => {
                        this.handleAPIErrors(response)
                    },
                );
            }
        },
        mounted() {

            if (this.userData) {
                this.setUserData(this.userData);
                this.loadPrefixesData();
                this.loadMemberOrganization(this.user.member_organisation).finally(() => {
                    this.isLoading = false;
                })

            } else {
                this.loadUserData().then(() => {
                    this.loadPrefixesData();
                    return this.loadMemberOrganization(this.user.member_organisation)
                }).finally(() => {
                    this.isLoading = false;
                });
            }


        },
        filters: {},
        components: {
            ActivatePrefixModal,
            InlineTextEditField,
            SpinnerIndicator
        }
    }

</script>

<style lang="scss">
    /* active prefix start */
    #active-prefix {
        color: white;
        background-color: #F26334;
        border: 1px solid #888b8d;
        padding: 10px;
        .active-prefix-score {
            padding-right: 20px;
        }
    }

    /* active prefix finish */

    /* ranges start */
    #ranges-table {
        border-style: solid;
        border-width: 1px;
        .panel-heading {
            color: white;
        }
        td {
            vertical-align: middle;
        }
        .col-description {
            width: 30%;
        }
        .gtin-part-highlight {
            color: #F26334;
        }
        .prefix-gtin {
            font-weight: bold;
            letter-spacing: 2px;
        }
    }

    .prefix-star-col {
        width: 20px;
        font-size: 20pt;
    }

    .prefix-star:before {
        color: #e1c51f;
        content: "\2606";
    }

    .prefix-star:hover:before {
        color: #e17f00;
        content: "\2605";
    }

    .prefix-star.prefix-star-set:before {
        color: #e1c51f;
        content: "\2605";
    }

    .prefix-star.prefix-star-set:hover:before {
        color: #b8b8b8;
        content: "\2605";
    }

    /* ranges finish */

    /* summary start */
    .account-summary {
        margin-top: 20px;
        border-style: solid;
        border-width: 1px;
        .panel-heading {
            color: white;
        }
    }

    .prefix-spinner
    {
        margin-top: 50px;
        margin-bottom: 50px;
    }

    /* summary finish */
</style>
