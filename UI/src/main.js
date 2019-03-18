// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from "vue";
import BootstrapVue from "bootstrap-vue";
import TitlePlugin from "@/components/Layout/PageTitle/TitlePlugin";
import VueBreadcrumbs from "vue-breadcrumbs";
import VueI18n from "vue-i18n";
import Vuelidate from "vuelidate";
import Router from "vue-router";
import axios from "axios";
import VueAxiosPlugin from "./services/axios.plugin";
import App from "./App";
import router from "./router";
import "./router/auth";
import store from "./store/";
import initAxios from "./services/init";
import VueLocalStorage from "vue-localstorage";
import CommonComponents from "./components/Common/CommonInstall";
import VueResource from 'vue-resource';

Vue.config.productionTip = false;

Vue.use(BootstrapVue);
Vue.use(TitlePlugin);
Vue.use(VueBreadcrumbs);
Vue.use(VueI18n);
Vue.use(Vuelidate);
Vue.use(Router);
Vue.use(VueAxiosPlugin, axios);
Vue.use(CommonComponents);
Vue.use(VueResource);
Vue.use(VueLocalStorage)


const i18n = new VueI18n({
    locale: window.localStorage.language || "en",
    messages: {
        en: require("./locales/en.json"),
        de: require("./locales/de.json"),
        fr: require("./locales/fr.json"),
        sv: require("./locales/sv.json")
    }
});


const tokenEl = document.getElementById('auth_token');
const isImpersonateEl = document.getElementById('is_impersonate');
if (tokenEl) {
    store.dispatch('auth/loginDjango');
    if (isImpersonateEl.value) {
        store.commit('auth/setImpersionate', isImpersonateEl.value);
    }
}
/* eslint-disable no-new */
new Vue({
    el: "#app",
    router,
    template: "<App/>",
    components: {App},
    i18n,
    store,
    created() {
        initAxios({router: this.$router, store});
    },
    mounted() {
        this.$store.dispatch("auth/inspectToken");
        setTimeout(() => {
            this.$store.dispatch("auth/inspectToken");
        }, 300000);
    }
});