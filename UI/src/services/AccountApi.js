import axios from 'axios'
import _ from 'lodash'

export default {
  register(data) {
    return axios.post('/api/v1/register/', _.pickBy(data)).then((response) => {
      return axios.get(response.data)
    }).then((response) => {
      return response.data
    })
  }

}
