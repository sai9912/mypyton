export default function plugin(Vue, axios) {

    if (plugin.installed) {
        return
    }
    plugin.installed = true

    if (!axios) {
        console.error('You have to install axios')
        return
    }

    Vue.axios = axios

    Object.defineProperties(Vue.prototype, {
        axios: {
            get() {
                return axios
            }
        }

    })
}