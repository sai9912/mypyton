import { createLocalVue, shallow, mount, TransitionStub, config, TransitionGroupStub } from '@vue/test-utils';
import TokenService from '../../../src/common/services/TokenService';
import Chance from 'chance';
import ApiMock from '../../common/api-mock.js';
import _ from 'lodash';
import PackagingLevelStep from '../../../src/productcreate/components/PackagingLevelStep.vue';
import VueRouter from 'vue-router';
import store from '../../../src/productcreate/store/index';
import * as AppRouter from '../../../src/productcreate/router/';
import mocksHelper from '../mocks'

const chance = new Chance();
let getElementByIdOld = document.getElementById;

describe('PackagingLevelStep', () => {
    let wrapper;
    let server;
    let localVue;
    let router;
    let initialState;
    beforeEach(() => {
        initialState = _.cloneDeep(store.state);
    });
    ['0' + '0' + chance.word({length: 12}), chance.word({length: 14})].forEach(testGtin => {
        describe(`gtin ${testGtin}`, () => {
            beforeEach(done => {
                mocksHelper.mockHTML(testGtin);
                router = new VueRouter({routes: [
                    {path: '/', component: PackagingLevelStep},
                    {path: '/packagingType', component: {render: h => '-'}},
                ]})
                router.replace('/')
                AppRouter.default = router;
                let $route = { path: '/' }
                localVue = createLocalVue();
                //localVue.use(VueRouter);
                server = sinon.createFakeServer();
                server.respondImmediately = true;
                ApiMock.mock(server)
                ApiMock.mockUser(server)
                store.replaceState(_.cloneDeep(initialState));
                wrapper = shallow(PackagingLevelStep, {
                    localVue,
                    router,
                    store,
                    mocks: {}
                });
                store.dispatch('ProductCreation/load');
                setTimeout(() => {
                    done();
                });
            });
            afterEach(done => {
                document.getElementById = getElementByIdOld;
                done();
            });
            it('next', done => {
                wrapper.vm.next();
                setTimeout(() => {
                    expect(router.currentRoute.path).to.equal('/packagingType');
                    done();
                }, 0);
            });
            it('packageLevel', done => {
                let level = chance.natural();
                wrapper.vm.packageLevel = level;
                setTimeout(() => {
                    expect(store.state.ProductCreation.packageLevel).to.equal(level);
                    done();
                }, 0);
            })
        })
    });
});
