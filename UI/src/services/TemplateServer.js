import axios from 'axios'

export default {
  getList(param) {
    return axios.get('/api/v1/templates', param).then((response) => {
      return response.data
    })
  }
}
