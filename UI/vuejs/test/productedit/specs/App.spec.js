import Vue from 'vue'
import Chance from 'chance'

const chance = new Chance();
let TokenService;
let getElementByIdOld = document.getElementById;

describe('prodedit App.vue', () => {
    beforeEach(done => {
        TokenService = require('../../../src/common/services/TokenService').default;
        TokenService.redirect = sinon.spy();
        done();
    });
    afterEach(done => {
        delete require.cache[require.resolve('../../../src/common/services/TokenService')];
        delete require.cache[require.resolve('../../../src/productedit/index.js')];
        document.getElementById = getElementByIdOld;
        done();
    });
    describe('test module loading', () => {
        let instance;
        beforeEach(() => {
            instance = require('../../../src/productedit/index.js').default
        });
        it('VueResource', done => {
            expect(instance.$http).to.be.an('function')
            done();
        });
        afterEach(() => {
            delete require.cache[require.resolve('../../../src/common/services/TokenService')];
            delete require.cache[require.resolve('../../../src/productedit/index.js')];
        });
    });
    it('redirect to login when the token is empty', done => {
        let instance = require('../../../src/productedit/index.js').default;
        assert(TokenService.redirect.calledWith(TokenService.loginUrl));
        done();
    });
    it('use token for http header', done => {
        let testToken = chance.word({length: 20});
        let xhr = sinon.useFakeXMLHttpRequest();
        xhr.onCreate = function (xhr) {
            xhr.send = () => {
                let headers = xhr.requestHeaders;
                expect(xhr.requestHeaders['Authorization']).to.equal('Token ' + testToken);
                done();
            };
        };
        let tokenEl = document.createElement('div');
        tokenEl.id = 'auth_token';
        tokenEl.innerHTML = testToken;
        document.getElementById = function(id) {
            if (id === 'auth_token') {
                return tokenEl;
            }
        };
        let instance = require('../../../src/productedit/index.js').default
        instance.$http.get('/test')
    });
})
