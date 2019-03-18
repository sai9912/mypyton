import { createLocalVue, shallow, mount, TransitionStub, config, TransitionGroupStub } from '@vue/test-utils';
import TokenService from '../../../src/common/services/TokenService';
import Chance from 'chance';
import ApiMock from '../../common/api-mock.js';
import _ from 'lodash';
import PackagingDetailsStep from '../../../src/productcreate/components/PackagingDetailsStep.vue';
import VueRouter from 'vue-router';
import store from '../../../src/productcreate/store/index';
import * as AppRouter from '../../../src/productcreate/router/';
import mocksHelper from '../mocks'

const chance = new Chance();
let getElementByIdOld = document.getElementById;

describe('PackagingDetailsStep', () => {
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
                    {path: '/', component: {render: h => '-'}},
                    {path: '/packagingType', component: {render: h => '-'}},
                    {path: '/details', component: PackagingDetailsStep}
                ]})
                router.replace('/details')
                AppRouter.default = router;
                localVue = createLocalVue();
                server = sinon.createFakeServer();
                server.respondImmediately = true;
                ApiMock.mock(server)
                ApiMock.mockUser(server)
                store.replaceState(_.cloneDeep(initialState));
                wrapper = shallow(PackagingDetailsStep, {
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
            it('prev', done => {
                wrapper.vm.prev();
                setTimeout(() => {
                    expect(router.currentRoute.path).to.equal('/packagingType');
                    done();
                }, 0);
            });
            _.each([
                ['country_of_origin', 'countries'],
                ['target_market', 'targetMarketList'],
                ['language', 'languageList']
            ], ([formKey, apiMockKey]) => {
                it(formKey, () => {
                    expect(wrapper.vm.formData[formKey].enum.length).to.equal(ApiMock[apiMockKey].length);
                });
            });
            it('gtin', done => {
                let value = chance.natural();
                wrapper.vm.gtin = value;
                setTimeout(() => {
                    expect(wrapper.vm.$store.state.ProductCreation.gtin).to.equal(value);
                    expect(wrapper.vm.gtin).to.equal(value);
                    done();
                }, 0);
            });
            //it('image', done => {
                //wrapper.vm.packageType = ApiMock.packaging[0].package_type;
                //setTimeout(() => {
                    //expect(wrapper.vm.image).to.equal(ApiMock.packaging[0].image_url);
                    //done();
                //}, 0);
            //});
            //it('description', done => {
                //wrapper.vm.packageType = ApiMock.packaging[0].package_type;
                //setTimeout(() => {
                    //expect(wrapper.vm.description).to.equal(ApiMock.packaging[0].ui_description);
                    //done();
                //}, 0);
            //});
        })
    });
});

