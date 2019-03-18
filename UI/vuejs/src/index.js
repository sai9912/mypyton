import Vue from 'vue';
import VueResource from 'vue-resource';

import Token from './common/services/TokenService';
import _ from 'lodash';
import Datatable from 'vue2-datatable-component/dist/min';
import BootstrapVue from 'bootstrap-vue';
import 'bootstrap-vue/dist/bootstrap-vue.css'
import "./common/initRaven"

import Dashboard from './dashboard/index';
import Create from './productcreate/index';
import Edit from './productedit/index';
import AdminDashboard from './admin_dashboard/index';
import ProductList from './productList/index';
import VueLocalStorage from 'vue-localstorage'

Vue.config.productionTip = true;
Vue.config.devtools = true;
Vue.use(VueResource);
Vue.use(BootstrapVue);
Vue.use(Datatable);
Vue.use(VueLocalStorage);

Token.init().then(response => {
    if (!Token.getToken()) {
        console.log('Invalid token, redirect to login');
        Token.redirectToLogin();
    }

    if (_.last(Vue.http.interceptors).custom) {
        Vue.http.interceptors.pop();
    }

    Vue.http.interceptors.push((request, next) => {
        request.headers.set('Authorization', 'Token ' + Token.getToken());

        next((response) => {
            return response;
        });
    });

    _.last(Vue.http.interceptors).custom = true;
    new Vue(Create);
    new Vue(Edit);
    new Vue(Dashboard);
    new Vue(AdminDashboard);
    new Vue(ProductList);
});

