import Vuex from 'vuex';
import Vue from 'vue';
import ProductCreation from './modules/ProductCreation';

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
      ProductCreation
  },
  strict: false
});

export default store;
