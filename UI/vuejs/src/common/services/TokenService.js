import Vue from "vue";

let _token = undefined;
export default {
    get _token() {
        return _token;
    },
    set _token(val) {
        _token = val;
    },
    init() {
        this._token = undefined;
        return Vue.http.get('/api/v1/accounts/login/').then(
            response => {
                this._token = response.body.token;
                return response.body;
            },
            response => {
                console.log('API Error:', response);
            },
        );
    },
    redirect(url) {
       window.location.assign(url)
    },
    loginUrl:  '/login',
    getToken() {
        return this._token;
    },
    redirectToLogin() {
        this.redirect(this.loginUrl)
    }
};
