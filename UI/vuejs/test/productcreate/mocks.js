import Chance from 'chance'
const chance = new Chance();

export default {
    token: chance.word({length: 30}),
    gcp: String(chance.natural()),
    gln_of_information_provider: chance.word({length: 20}),
    mockHTML(gtin) {
        let tokenEl = document.createElement('div');
        tokenEl.id = 'auth_token';
        tokenEl.innerHTML = this.token;
        let gcpEl = document.createElement('div');
        gcpEl.id = 'gcp';
        gcpEl.innerHTML = this.gcp;
        let formDataEl = document.createElement('div');
        formDataEl.id = 'FormAppData';
        formDataEl.innerHTML = JSON.stringify({
            gtin,
            gln_of_information_provider: this.gln_of_information_provider
        });
        document.getElementById = function(id) {
            if (id === 'auth_token') {
                return tokenEl;
            } else if (id === 'gcp') {
                return gcpEl;
            } else if (id === 'FormAppData') {
                return formDataEl;
            }
        };
    }

};
