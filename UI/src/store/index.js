import Vuex from 'vuex'
import Vue from 'vue'
import prefixes from './modules/prefixes'
import createPersistedState from 'vuex-persistedstate'
import auth from './modules/auth'
import accountApi from './modules/accountApi'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    auth,
    accountApi,
    prefixes
  },
  plugins: [createPersistedState(
    {
      paths: ['auth', 'prefixes.activePrefixId']
    }
  )],
  strict: false
})

export default store
