import axios from 'axios'

export default {
  getList(params = {}) {
    return axios.get('/api/v1/products', {params}).then((response) => {
      return response.data
    })
  },
  get(gtin) {
    return axios.get('/api/v1/products/' + gtin).then((response) => {
      return response.data
    })
  },
  create(data) {
    return axios.post('/api/v1/products', data).then((response) => {
      return response.data
    })
  },
  update(gtin, data) {
    return axios.put('/api/v1/products/' + gtin, data).then((response) => {
      return response.data
    })
  },
  patch(gtin, data) {
    return axios.patch('/api/v1/products/' + gtin, data).then((response) => {
      return response.data
    })
  },
  delete(gtin) {
    return axios.patch('/api/v1/products/' + gtin).then((response) => {
      return response.data
    })
  }
}
