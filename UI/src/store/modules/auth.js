import AuthService from '../../services/AuthService'
import moment from 'moment'

const state = {
    token: '',
    expired: null,
    nextRenew: null,
    userData: null,
    rememberMe: null,
    isAuth: false,
    needAcceptTerms: false,
    terms: null,
    isImpersionate: false,
    loginDjangoPending:false
}

const getters = {}

const mutations = {
    updateData(state, userData) {
        state.userData = userData
    },
    updateToken(state, newToken) {
        state.isAuth = true
        state.token = newToken
        state.expired = moment().add(24, 'hours').toDate()
        state.lastRenew = moment().add(1, 'hours').toDate()
    },
    rememberMe(state, rememberMe) {
        state.rememberMe = rememberMe
    },
    logout(state) {
        state.token = null
        state.userData = null
        state.isAuth = false
        state.needAcceptTerms = false
    },
    setTerms(state, payload) {
        state.terms = payload
    },
    setNeedAcceptTerms(state, payload) {
        state.needAcceptTerms = payload
    },
    setImpersionate(state, payload) {
        state.isImpersionate = payload
    },
    setLoginDjangoPending(state, payload) {
        state.loginDjangoPending = payload
    }
}

const actions = {
    async login({commit}, payload) {
        const result = await AuthService.login({
            username: payload.username,
            password: payload.password
        })
        commit('updateToken', result.token)
        commit('updateData', result.user)
        commit('rememberMe', payload.rememberMe)
        return result
    },
    async loginDjango({commit}) {
        commit('setLoginDjangoPending', true)
        try {
            const result = await AuthService.getLoginData()
            commit('updateToken', result.token)
            commit('updateData', result.user)
        }
        catch (ex) {

        }
        commit('setLoginDjangoPending', false)
    },
    async getTerms({commit, state}) {
        const terms = await AuthService.getTerms()
        commit('setTerms', terms)
        return terms
    },
    async checkTerms({commit, state, dispatch}) {
        const terms = await AuthService.getTerms()
        commit('setTerms', terms)
        if (!state.userData.agreed || !state.userData.agreed_version || moment(state.userData.agreed_version) < moment(terms.date_terms) || moment(state.userData.agreed_version) < moment(terms.date_terms_cloud)) {
            commit('setNeedAcceptTerms', true)
        }
    },
    async acceptTerms({commit, state}) {
        const result = await AuthService.patch(
            state.userData.email,
            {
                agreed: true,
                agreed_version: moment(state.terms.date_terms) < moment(state.terms.date_terms_cloud) ? state.terms.date_terms_cloud : state.terms.date_terms,
                agreed_date: moment().utc().format()
            })
        commit('setNeedAcceptTerms', false)
        return result
    },
    logout({commit}) {
        commit('logout')
    },
    inspectToken({commit, state}) {
        if (state.token && moment() < moment(state.expired) && moment() > moment(state.nextRenew)) {
            return AuthService.renew().then((result) => {
                commit('updateToken', result.token)
            })
        }
    }
}

export default {
    namespaced: true,
    state,
    getters,
    mutations,
    actions
}
