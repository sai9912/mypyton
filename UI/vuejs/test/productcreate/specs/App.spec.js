import { createLocalVue, shallow, mount, TransitionStub, config, TransitionGroupStub } from '@vue/test-utils';
import Vue from 'vue'
import Chance from 'chance'
import mocksHelper from '../mocks'
import ApiMock from '../../common/api-mock.js';
import Root from '../../../src/productcreate/components/Root.vue';
import store from '../../../src/productcreate/store/index';
import VueRouter from 'vue-router';

const chance = new Chance();
let TokenService;
let getElementByIdOld = document.getElementById;

describe('prodcreate App.vue', () => {
    beforeEach(done => {
        delete require.cache[require.resolve('../../../src/common/services/TokenService')];
        delete require.cache[require.resolve('../../../src/productcreate/index.js')];
        TokenService = require('../../../src/common/services/TokenService').default;
        TokenService.redirect = sinon.spy();
        done();
    });
    afterEach(done => {
        delete require.cache[require.resolve('../../../src/common/services/TokenService')];
        delete require.cache[require.resolve('../../../src/productcreate/index.js')];
        document.getElementById = getElementByIdOld;
        done();
    });
    describe('test module loading', () => {
        let instance;
        beforeEach(() => {
            instance = require('../../../src/productcreate/index.js').default
        });
        it('VueResource', done => {
            expect(instance.$http).to.be.an('function')
            done();
        });
        afterEach(() => {
            delete require.cache[require.resolve('../../../src/common/services/TokenService')];
            delete require.cache[require.resolve('../../../src/productcreate/index.js')];
        });
    });
    it('redirect to login when the token is empty', done => {
        let instance = require('../../../src/productcreate/index.js').default;
        assert(TokenService.redirect.calledWith(TokenService.loginUrl));
        done();
    });
    it('use token for http header', done => {
        let xhr = sinon.useFakeXMLHttpRequest();
        xhr.onCreate = function (xhr) {
            xhr.send = () => {
                let headers = xhr.requestHeaders;
                expect(xhr.requestHeaders['Authorization']).to.equal('Token ' + mocksHelper.token);
                done();
            };
        };
        mocksHelper.mockHTML();
        let instance = require('../../../src/productcreate/index.js').default
        instance.$http.get('/test')
    });
    describe('load initial state', () => {
        let instance;
        let gtin = chance.word({length: 30});
        beforeEach(done => {
            let server = sinon.createFakeServer();
            server.respondImmediately = true;
            ApiMock.mock(server);
            ApiMock.mockUser(server);
            mocksHelper.mockHTML(gtin);
            let router = new VueRouter({routes: [
            ]})
            const $route = { path: '/' }
            let localVue = createLocalVue();
            localVue.use(VueRouter);
            instance = mount(Root, {
                localVue,
                store,
                router
            });
            setTimeout(() => {
                done();
            });
        });
        [
            ['packageTypeList', 'packaging'], ['packageLevelList', 'templates']
        ].forEach(([stateKey, apiMockKey]) => {
            it(stateKey, () => {
                expect(instance.vm.$store.state.ProductCreation[stateKey].length).to.equal(ApiMock[apiMockKey].length);
            })
        });
        it('gtin', () => {
            expect(instance.vm.$store.state.ProductCreation.gtin).to.equal(gtin);
        });
        it('gln_of_information_provider', () => {
            expect(instance.vm.$store.state.ProductCreation.gln_of_information_provider).to.equal(mocksHelper.gln_of_information_provider);
        });
        it('gcp', () => {
            expect(instance.vm.$store.state.ProductCreation.gcp).to.equal(mocksHelper.gcp);
        });
    });
})

