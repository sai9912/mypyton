<template>
    <div>
        <b-alert show variant="danger" v-for="error in non_field_errors">
            {{ error }}
        </b-alert>

        <div class="row admin-links">
            <div class="col-6">
                <ul>
                    <li>
                        <!-- todo: urls transfer api from backend to vue -->
                        <a href="/admin/member_organisations/memberorganisationowner/mo_admin/">
                            Full administration interface
                        </a>
                    </li>
                    <li>
                        <a :href="`/admin/member_organisations/memberorganisationowner/mo_admin/member_organisations/memberorganisation/${user.member_organisation_id}/change/`">
                            Member organisation settings
                        </a>
                    </li>
                </ul>
            </div>
        </div>

        <div class="row admin-links">
            <div class="col-4">
                <h3>{{ gettext('Search') }}</h3>
                <ul>
                    <li>
                        <a href="/admin/member_organisations/memberorganisationowner/mo_admin/company_organisations/companyorganisation/">
                            {{ gettext('Companies') }}
                        </a>
                    </li>
                    <li>
                        <a href="/admin/member_organisations/memberorganisationowner/mo_admin/prefixes/prefix/">
                            {{ gettext('Prefixes') }}
                        </a>
                    </li>
                    <li>
                        <a href="/admin/member_organisations/memberorganisationowner/mo_admin/company_organisations/companyorganisationuser/">
                            {{ gettext('Users') }}
                        </a>
                    </li>
                    <li>
                        <a href="/admin/member_organisations/memberorganisationowner/mo_admin/products/product/">
                            {{ gettext('Products') }}
                        </a>
                    </li>
                </ul>
            </div>
            <div class="col-4">
                <h3>{{ gettext('Report') }}</h3>
                <ul>
                    <li>
                        <a href="#" @click.prevent="fileExport('/admin/member_organisations/memberorganisationowner/mo_admin/company_organisations/companyorganisation/', 'export_as_csv')">
                            {{ gettext('Companies') }}
                        </a>
                    </li>
                    <li>
                        <a href="#" @click.prevent="fileExport('/admin/member_organisations/memberorganisationowner/mo_admin/prefixes/prefix/', 'export_as_csv')">
                            {{ gettext('Prefixes') }}
                        </a>
                    </li>
                    <li>
                        <a href="#" @click.prevent="fileExport('/admin/member_organisations/memberorganisationowner/mo_admin/company_organisations/companyorganisationuser/', 'export_as_csv')">
                            {{ gettext('Users') }}
                        </a>
                    </li>
                    <li>
                        <a class="text-muted" href="#">
                            {{ gettext('Products') }}
                        </a>
                    </li>
                </ul>
            </div>
            <div class="col-4">
                <h3>{{ gettext('Import Data') }}</h3>
                <ul>
                    <li>
                        <a href="javascript:void('')" @click="showImportModal('companies')">
                            {{ gettext('Companies') }}
                        </a>
                    </li>
                    <li>
                        <a href="javascript:void('')" @click="showImportModal('prefixes')">
                            {{ gettext('Prefixes') }}
                        </a>
                    </li>
                    <li>
                        <a href="javascript:void('')" @click="showImportModal('users')">
                            {{ gettext('Users') }}
                        </a>
                    </li>
                </ul>
            </div>
        </div>

        <import-file-modal ref="importFileDialog"></import-file-modal>
    </div>
</template>


<script>
    import APIService from '../../common/services/APIService';
    import ImportFileModal from "../components/ImportFileModal";

    import _ from 'lodash';
    import default_state from '../default_state';

    export default {
        data() {
            // if you don't see an expected variable,
            // check 'default_state.json', it must be specified there with an initial value
            return {
                ...default_state,
            };
        },
        computed: {},
        watch: {},
        methods: {
            gettext(text) {
                return gettext(text);
            },
            showImportModal(type) {
                let import_parameters = {
                    'companies': {
                        title: gettext('Import Companies'),
                        api_url: '/api/v1/companies/upload/__MO__/',
                    },
                    'prefixes': {
                        title: gettext('Import Prefixes'),
                        api_url: '/api/v1/prefixes/upload/__MO__/'
                    },
                    'users': {
                        title: gettext('Import Users'),
                        api_url: '/api/v1/users/upload/__MO__/'
                    },
                };

                let api_url = import_parameters[type].api_url.replace(
                    '__MO__', this.user.member_organisation
                );
                this.$refs.importFileDialog.open(
                    import_parameters[type].title,
                    api_url
                );
            },
            loadUserData() {
                return this.$http.get(`/api/v1/accounts/login/`).then(
                    response => {
                        // setting user data
                        if (_.isObject(_.get(response, 'body.user'))) {
                            _.forEach(this.user, (value, key) => {
                                let api_value = response.body.user[key];
                                if (api_value !== undefined && !_.isObject()) {
                                    // only plain values will be assigned
                                    this.user[key] = api_value;
                                }
                            })
                        }
                        // setting prefix data
                        if (_.isObject(_.get(response, 'body.user.product_active_prefix'))) {
                            _.forEach(this.product_active_prefix, (value, key) => {
                                let api_value = response.body.user.product_active_prefix[key];
                                if (api_value !== undefined) {
                                    this.product_active_prefix[key] = api_value;
                                }
                            })
                        }
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
            getCookie(name) {
                let matches = document.cookie.match(new RegExp(
                    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
                ));
                return matches ? decodeURIComponent(matches[1]) : undefined;
            },
            convertToFormData(data) {
                let form_data = new FormData();
                _.forOwn(data, (field_value, field_name) => {
                    form_data.set(field_name, field_value);
                });
                return form_data;
            },
            downloadContentFile(file_response) {
                let element = document.createElement('a');
                let content_type = file_response.headers.map['content-type'][0];
                let file_name = file_response.headers.map['content-disposition'][0];
                file_name = file_name.match(/filename=(.+)/);
                file_name = file_name ? file_name[1] : 'downloaded_file.txt';

                element.setAttribute(
                    'href', `data:${content_type},${encodeURIComponent(file_response.body)}`
                );
                element.setAttribute('download', file_name);
                element.style.display = 'none';

                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
            },
            fileExport(target_url, action) {
                let post_data = {
                    'action': action,
                    'csrfmiddlewaretoken': this.getCookie('csrftoken'),
                    // doesn't matter export should be performed for all items
                    '_selected_action': 9999,
                };

                this.$http.post(target_url, this.convertToFormData(post_data)).then(
                    response => {
                        this.downloadContentFile(response);
                    },
                    response => {
                        console.log('Error:', response);
                        this.handleAPIErrors(response);
                    },
                );
            },
            handleAPIErrors(response) {
                if (typeof response.body === 'string') {
                    this.non_field_errors = ['Internal Error. Please contact Support.'];
                } else if (Array.isArray(response.body)) {
                    this.non_field_errors = response.body;
                }
                console.log('API Error:', response.body);
            },
        },
        mounted() {
            this.loadUserData().then(() => {
                if (this.user.company_organisation) {
                    this.loadCompanyOrganisation(this.user.company_organisation);
                }
            });
        },
        filters: {},
        components: {
            ImportFileModal,
        }
    }

</script>

<style lang="scss">
    .admin-links {
        ul {
            padding-top: 10px;
            padding-left: 20px;
            font-size: 12pt;
        }
    }
</style>
