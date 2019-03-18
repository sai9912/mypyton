import AccountApi from '../../services/AccountApi'

const state = {}

const getters = {}

const mutations = {}

const actions = {
  register(state, payload) {
    return AccountApi.register(payload).then((result) => {
      this.commit('auth/updateToken', result.token)
      this.commit('auth/updateData', result.user)
      this.commit('auth/rememberMe', true)
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
