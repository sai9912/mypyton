import axios from 'axios'

export default {
  getList() {
    return axios.get('/api/v1/countries_of_origin').then((response) => {
      return response.data
    })
  }
}
