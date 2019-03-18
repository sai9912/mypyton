import axios from 'axios'
export default {
  getList() {
    return axios.get('/api/v1/prefixes').then((response) => {
      return response.data
    })
  },
  get(prefix) {
    return axios.get('/api/v1/prefixes/' + prefix).then((response) => {
      return response.data
    })
  },
  create(data) {
    return axios.post('/api/v1/prefixes', data).then((response) => {
      return response.data
    })
  },
  update(prefix, data) {
    return axios.put('/api/v1/prefixes/' + prefix, data).then((response) => {
      return response.data
    })
  },
  patch(prefix, data) {
    return axios.patch('/api/v1/prefixes/' + prefix, data).then((response) => {
      return response.data
    })
  },
  delete(prefix) {
    return axios.patch('/api/v1/prefixes/' + prefix).then((response) => {
      return response.data
    })
  },
  getProducts(prefix) {
    return axios.get('/api/v1/prefixes/' + prefix + '/products').then((response) => {
      return response.data
    })
  },
  createProduct(prefix) {
    return axios.post('/api/v1/prefixes/' + prefix + '/products').then((response) => {
      return response.data
    })
  },
  action(prefix) {
    return axios.put('/api/v1/prefixes/' + prefix + '/action').then((response) => {
      return response.data
    })
  },
  partialAction(prefix) {
    return axios.patch('/api/v1/prefixes/' + prefix + '/action').then((response) => {
      return response.data
    })
  }

}
