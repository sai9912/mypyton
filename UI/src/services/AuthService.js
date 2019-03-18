import axios from 'axios'

export default {
    login(data) {
        return axios.post('/api/v1/accounts/login/', data).then((response) => {
            return response.data
        })
    },
    getLoginData(data) {
        return axios.get('/api/v1/accounts/login/', data).then((response) => {
            return response.data
        })
    },
    renew() {
        return axios.post('/api/v1/accounts/renew/').then((response) => {
            return response.data
        })
    },
    getTerms() {
        return axios.get('/api/v1/accounts/terms/').then((response) => {
            return response.data
        })
    },
    update(username, data) {
        return axios.put('/api/v1/accounts/profile/' + username, data).then((response) => {
            return response.data
        })
    },
    patch(username, data) {
        return axios.patch('/api/v1/accounts/profile/' + username, data).then((response) => {
            return response.data
        })
    }
}
