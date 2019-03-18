import Vue from 'vue';

export default {
    getList(params) {
        return Vue.http.get('/api/v1/gpc/', {params}).then((response) => {
            return response.body
        })
    }
}
