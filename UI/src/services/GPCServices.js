import axios from 'axios'

export default {
  getList(params) {
    return axios.get('/api/v1/gpc', {params}).then((response) => {
      return response.data
    })
  }
}
