import axios from 'axios'

export default {
    getList() {
        return axios.get('/api/v1/ui-languages/')
            .then((response) => {
                return response.data
            })
    },
    selectLanguage(data) {
        return axios.post('/api/v1/ui-languages/', data)
            .then((response) => {
                return response.data
            })
    }

}
