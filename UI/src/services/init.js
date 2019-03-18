import Vue from 'vue'
import  axios from "axios";

export default ({router, store}) => {
    axios.interceptors.request.use(function (config) {
        console.log(config)
        const token = store.state.auth.token
        if (token) {
            config.headers.Authorization = `Token ${token}`
        }
        return config
    }, function (err) {
        return Promise.reject(err)
    })

    axios.interceptors.request.use((config) => {
        if (config.method !== 'patch' && config.method !== 'put' && config.url[config.url.length - 1] !== '/') {
            config.url += '/'
        }
        return config
    })
    axios.interceptors.response.use(function (response) {
        return response
    }, function (error) {
        if (error.response.status === 401) {
            store.dispatch('auth/logout')
            router.push('login')
        }
        return Promise.reject(error)
    })

    Vue.http.interceptors.push((request, next) => {
        const token = store.state.auth.token
        request.headers.set('Authorization', 'Token ' + token);

        next((response) => {
            return response;
        });
    });
}
