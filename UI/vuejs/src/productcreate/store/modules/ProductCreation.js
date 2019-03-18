import router from '../../router/';
import Vue from 'vue';
import _ from 'lodash';
import APIService from '../../../common/services/APIService';
import TranslationService from '../../../common/services/TranslationService';
import AuthService from "../../../common/services/AuthService";

const state = {
    packageTypeList: [],
    packageLevelList: [],
    countryList: [],
    targetMarketList: [],
    languageList: [],
    language: undefined,
    fallbackLanguages: [],
    loading: true,
    stepIdx: 0,
    packageLevel: 70,
    packageType: undefined,
    gtin: undefined, //initial
    gcp: undefined,
    gln_of_information_provider: undefined,
    summaryData: null,
    moInfo: {},
};

const getters = {
    getTranslated: (state) => (i18n_field) => {
        let translated_value = TranslationService.getTranslated(
            i18n_field, state.language, state.fallbackLanguages
        );
        return translated_value || '--';
    }
};

const mutations = {
    setPackageLevel(state, level) {
        state.packageLevel = _.parseInt(level);
    },
    setGtin(state, val) {
        state.gtin = val;
    },
    setInfo(state, infoObj) {
        _.each([
            'packageTypeList', 'packageLevelList', 'gtin', 'gln_of_information_provider', 'gcp',
            'countryList', 'targetMarketList', 'languageList', 'language', 'fallbackLanguages',
            'moInfo',
        ], key => {
            if (!_.isUndefined(infoObj[key])) {
                state[key] = infoObj[key];
            }
        });
    },
    setInitialPackageType(state) {
        state.packageType = state.packageTypeList.length > 0 && state.packageTypeList[0].id || null;
    },
    setStep(state, stepIdx) {
        state.stepIdx = stepIdx;
    },
    setLoading(state, loading) {
        state.loading = loading;
    },
    setSummaryData(state, payload) {
        state.summaryData = payload;
    },
    setSubproducts(state, subproducts) {
        state.subproducts = subproducts;
    },
    setPackageType(state, packageType) {
        state.packageType = packageType
    }
};

const stepRouteList = ['/', '/packagingType', '/details'];

const actions = {
    nextStep({state, commit}) {
        if (state.packageLevel != 70 && state.stepIdx == 1) {
            document.location.href = '/products/subproduct/add/case/?gtin=' + state.gtin + '&package_level=' + state.packageLevel + '&package_type=' + state.packageType
        } else {
            router.push(stepRouteList[state.stepIdx + 1]);
            commit('setStep', state.stepIdx + 1);
        }
    },
    prevStep({state, commit}) {
        router.push(stepRouteList[state.stepIdx - 1]);
        commit('setStep', state.stepIdx - 1);
    },
    showSummaryData({state, commit}, payload) {
        commit('setSummaryData', payload);
        router.push('/summary');
    },
    load({state, commit}) {
        let formDataStr = document.getElementById('FormAppData').innerHTML;
        let formData = JSON.parse(formDataStr);

        commit('setLoading', true);
        let promiseList = [
            APIService.getPackagingTypes(formData['language'], formData['mo_slug']),
            APIService.getPackagingLevels(formData['language'], formData['mo_slug']),
            APIService.getMemberOrganisation(formData['mo_slug']),
            AuthService.getLogin()
        ];

        Promise.all(promiseList).then(([packageTypeList, packageLevelList, moInfo, loginInfo]) => {
            commit('setInfo', {
                packageTypeList: packageTypeList.sort((a, b) => a.order - b.order),
                packageLevelList,
                gtin: formData['gtin'],
                gln_of_information_provider: formData['gln_of_information_provider'],
                gcp:loginInfo.user.product_active_prefix.prefix,
                language: formData['language'],
                fallbackLanguages: formData['fallback_languages'],
                moInfo: moInfo,
            });
            if(!state.packageType)
            {
                commit('setInitialPackageType');
            }
        }).finally(() => {
            commit('setLoading', false)
        });
        let idx = stepRouteList.indexOf(router.currentRoute.path);
        if (idx > -1) {
            commit('setStep', idx);
        }
    }
};

export default {
    namespaced: true,
    state,
    getters,
    mutations,
    actions
}
