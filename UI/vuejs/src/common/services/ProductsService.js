import Vue from 'vue';

export default {
  getList(params = {}) {
    return Vue.http.get('/api/v1/products/', {params}).then((response) => {
      return response.data
    })
  },
  get(gtin) {
    return Vue.http.get('/api/v1/products/' + gtin).then((response) => {
      return response.data
    })
  },
  create(data) {
    return Vue.http.post('/api/v1/products', data).then((response) => {
      return response.data
    })
  },
  update(gtin, data) {
    return Vue.http.put('/api/v1/products/' + gtin, data).then((response) => {
      return response.data
    })
  },
  patch(gtin, data) {
    return Vue.http.patch(`/api/v1/products/${gtin}/`, data).then((response) => {
      return response.data
    })
  },
  delete(gtin) {
    return Vue.http.patch('/api/v1/products/' + gtin).then((response) => {
      return response.data
    })
  }
}
