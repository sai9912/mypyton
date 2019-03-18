import Vue from 'vue';

export default {
    getAllUom(viewMask) {
        const promises = [];
        const resultObject = {};
        if (viewMask.measures.isDimension) {
            promises.push(this.getDimensions().then((result) => {
                resultObject.dimensions = result;
            }))
        }
        if (viewMask.measures.isWeight) {
            promises.push(this.getWeights().then((result) => {
                resultObject.weights = result;
            }))
        }
        if (viewMask.measures.isNet) {
            promises.push(this.getNetContent().then((result) => {
                resultObject.netContent = result;
            }))
        }
        return Promise.all(promises).then((result) => {
            return resultObject;
        })
    },

    getDimensions() {
        return Vue.http.get('/api/v1/dimensions_uom/', {}).then((response) => {
            return response.body
        })
    },

    getWeights() {
        return Vue.http.get('/api/v1/weights_uom/', {}).then((response) => {
            return response.body
        })
    },

    getNetContent() {
        return Vue.http.get('/api/v1/net_content_uom/', {}).then((response) => {
            return response.body
        })
    }
}
