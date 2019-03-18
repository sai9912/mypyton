import Vue from 'vue';
import _ from 'lodash';

export default {
    getMemberOrganisation(mo_slug) {
        return Vue.http.get(`/api/v1/member_organisations/${mo_slug}/`).then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return {};
        });
    },
    getCompanyOrganisation(co_slug) {
        return Vue.http.get(`/api/v1/companies/${co_slug}/`).then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return {};
        });
    },
    getPrefixes() {
        return Vue.http.get(`/api/v1/prefixes/`).then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    },
    getCountries() {
        return Vue.http.get('/api/v1/countries_of_origin/').then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    },
    getPackagingTypes(lang_slug, mo_slug) {
        let lang = lang_slug = lang_slug ? lang_slug : 'en';

        return Vue.http.get(`/api/v1/packaging/?lang=${lang}&mo=${mo_slug}`).then(response => {
            if (_.hasIn(response, 'body')) {
                return _(response.body).map(packagingData => {
                    let label_i18n = JSON.parse(packagingData.ui_label_i18n);
                    return {
                        id: packagingData.package_type,
                        image_url: packagingData.image_url,
                        label_i18n: label_i18n,
                        description_i18n: JSON.parse(packagingData.ui_description_i18n),
                        name: label_i18n,
                        order: packagingData.order
                    };
                }).sortBy(['id']).value()
            }
            return [];
        });
    },
    getPackagingLevels(lang_slug, mo_slug) {
        let lang = lang_slug = lang_slug ? lang_slug : 'en';

        return Vue.http.get(`/api/v1/templates/?lang=${lang}&mo=${mo_slug}`).then(response => {
            if (_.hasIn(response, 'body')) {
                return _(response.body).map(template => {
                    return {
                        id: template.package_level,
                        name: template.name,
                        template_id: template.id,
                        image_url: template.image_url,
                        label_i18n: JSON.parse(template.ui_label_i18n),
                    };
                }).sortBy(['id']).reverse().value()
            }
            return [];
        });
    },
    getTemplateWithAttributes(template_id) {
        return Vue.http.get(`/api/v1/templates/${template_id}/`).then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    },
    getTargetMarkets() {
        return Vue.http.get('/api/v1/target_markets/').then(response => {
            if (_.hasIn(response, 'body')) {
                return _(response.body).map(marketData => {
                    return {
                        id: marketData.id,
                        code: marketData.code,
                        name: marketData.market,
                    };
                }).sortBy(['id']).value();
            }
            return [];
        });
    },
    getLanguages() {
        return Vue.http.get('/api/v1/languages/').then(response => {
            if (_.hasIn(response, 'body')) {
                return  _(response.body).map(langData => {
                    return {
                        id: langData.id,
                        slug: langData.slug,
                        name: langData.name,
                    };
                }).sortBy(['id']).value();
            }
            return [];
        });
    },
    getDefaults() {
        return Vue.http.get(`/api/v1/defaults/`).then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    },
    getSubproducts(gtin) {
        return Vue.http.get(`/api/v1/products/${gtin}/subproducts/`).then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    },
    subproductCreate(product_gtin, subproduct_gtin, quantity) {
        console.log('subproductCreate', product_gtin, subproduct_gtin, quantity)
        return Vue.http.post(`/api/v1/products/${product_gtin}/subproducts/${subproduct_gtin}/`, {quantity: quantity})
                       .then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    },
    subproductEditQuantity(product_gtin, subproduct_gtin, quantity) {
        console.log('subproductEditQuantity', product_gtin, subproduct_gtin, quantity)
        return Vue.http.patch(`/api/v1/products/${product_gtin}/subproducts/${subproduct_gtin}/`, {quantity: quantity})
                       .then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    },
    subproductDelete(product_gtin, subproduct_gtin) {
        console.log('subproductDelete', product_gtin, subproduct_gtin)
        return Vue.http.delete(`/api/v1/products/${product_gtin}/subproducts/${subproduct_gtin}/`)
                       .then(response => {
            if (_.hasIn(response, 'body')) {
                return response.body;
            }
            return [];
        });
    }
};
