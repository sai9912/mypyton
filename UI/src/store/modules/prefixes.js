import PrefixesService from '../../services/PrefixesService'

const state = {
  loading: false,
  prefixes: [],
  activePrefix: '53920001052',
  activePrefixId: null,
  productsAllocated: 3,
  productAvailable: 10,
  locationAllocated: 1,
  locationAvailable: 3
}

const getters = {}

const mutations = {
  updatePrefixes(state, prefixes) {
    state.prefixes = prefixes
  },
  setActivePrefix(state, prefix) {
    state.activePrefix = prefix
    state.activePrefixId = prefix.prefix
  },
  resetActivePrefix(state) {
    state.activePrefix = null
    state.activePrefixId = null
  },
  setLoading(state, loading) {
    state.loading = loading
  }
}

const actions = {
  loadPrefixes({commit, state}) {
    commit('setLoading', true)
    return PrefixesService.getList().then((result) => {
      commit('updatePrefixes', result)
      if (result.length > 0) {
        const savedPrefix = state.activePrefixId && result.find((item) => item.id === state.activePrefixId)
        if (savedPrefix) {
          commit('setActivePrefix', savedPrefix)
        } else {
          commit('setActivePrefix', result[0])
        }
      } else {
        commit('resetActivePrefix')
      }
    }).finally(() => {
      commit('setLoading', false)
    })
  },
  selectPrefix({commit}, payload) {
    commit('setActivePrefix', payload)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
