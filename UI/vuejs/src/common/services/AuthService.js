import Vue from 'vue';

export default {
    getLogin() {
        return Vue.http.get('/api/v1/accounts/login/', {}).then((response) => {
            return response.body
        })
    }
}
