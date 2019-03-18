import { createLocalVue, shallow, mount, TransitionStub, config, TransitionGroupStub } from '@vue/test-utils'
import TokenService from '../../../src/common/services/TokenService'
import Root from '../../../src/productedit/components/Root.vue'
import Chance from 'chance'
import ApiMock from '../../common/api-mock.js'
import _ from 'lodash'

const chance = new Chance();

let testSummary = chance.word({length: 30});
let getElementByIdOld = document.getElementById;
let localVue;
let testGtin = '1' + '0' + chance.word({length: 12});
let testPackageType = chance.natural();
let testId = chance.natural();
let prodData = {
    id: chance.natural(),
    country_of_origin: chance.natural(),
    target_market: chance.natural(),
    language: chance.natural(),
    package_type: testPackageType,
    gtin: chance.string({length: 15, pool: '1234567890'})
};
let fieldNameList = [
    'gln_of_information_provider', 'company', 'label_description', 'brand', 'sub_brand',
    'functional_name', 'variant', 'description', 'category', 'sku', 'is_bunit', 'is_cunit',
    'is_dunit', 'is_vunit', 'is_iunit', 'is_ounit',  'gross_weight', 'net_weight', 'depth',
    'width', 'height', 'website_url', 'net_content', 'gs1_cloud_state'
];
_.each(fieldNameList, (fieldName) => {
    prodData[fieldName] = chance.word({length: 20})
})

let barcodeList = ['EAN13', 'UPCA', 'ITF14'];


describe('prodedit Root.vue', () => {
    afterEach(done => {
        document.getElementById = getElementByIdOld;
        done();
    });
    beforeEach(done => {
        localVue = createLocalVue();
        let gtinEl = document.createElement('div');
        gtinEl.innerHTML = testGtin;
        let formDataEl = document.createElement('div');
        formDataEl.innerHTML = JSON.stringify({
            kind: 'test_kind',
            prefix: 'test_prefix',
            user_company: 'test_user_company',
            barcodes: 'test_barcodes',
            form_data: {
                language: 'test_language',
                gross_weight_uom: 'test_gross_weight_uom',
                net_weight_uom: 'test_net_weight_uom',
                depth_uom: 'test_depth_uom',
                width_uom: 'test_width_uom',
                height_uom: 'test_height_uom',
                net_content_uom: 'test_net_content_uom'
            }
        });
        document.getElementById = (id) => {
            if (id === 'bcm-gtin') {
                return gtinEl;
            } else if (id === 'FormAppData') {
                return formDataEl;
            }
        };
        done();
    });
    [testGtin, '0' + '0' + chance.word({length: 12}), chance.word({length: 14})].forEach(gtin => {
        [4, 10, 40, 70, chance.natural()].forEach(testPackageLevel => {
            describe('mounted', () => {
                let barcodesQueried;
                beforeEach(() => {
                    prodData['package_level'] = testPackageLevel;
                    prodData['gtin'] = gtin;
                    barcodesQueried = [];
                });
                describe(`package_level = ${testPackageLevel}, gtin = ${gtin}`, () => {
                    let wrapper;
                    let server;

                    beforeEach(done => {
                        server = sinon.createFakeServer();
                        server.respondImmediately = true;
                        server.respondWith('GET', /\/api\/v1\/products\/(\w+)\//, (xhr, gtin) => {
                            xhr.respond(200, {
                                'Content-Type': 'application/json'
                            }, JSON.stringify(_.cloneDeep(prodData)));
                        });
                        server.respondWith('GET', /\/products\/(\w+)\/view_summary\/\?(\w+)/, (xhr, gtin) => {
                            xhr.respond(200, {}, testSummary);
                        });
                        ApiMock.mock(server)
                        ApiMock.mockUser(server)

                        let barcodePromise = new Promise(resolveFn => {
                            server.respondWith(
                                'GET', /\/barcodes\/ajax\/(\w+)\/(\w+)\/preview\//, (xhr, val1, val2) => {
                                if (_.includes(barcodeList, val1) && val2) {
                                    xhr.respond(200, {}, val1 + '_test');
                                    barcodesQueried.push(val1);
                                    resolveFn();
                                }
                            });
                        });
                        wrapper = mount(Root, {
                            localVue,
                            stubs: {
                                'datatable': true
                            }
                        })
                        setTimeout(() => {
                            done();
                        });
                    });

                    it('Root.gtin == prodData.gtin', () => {
                        expect(wrapper.vm.gtin).to.equal(prodData.gtin);
                    });
                    it('prodData.gtin inc Root.gtin13', () => {
                        assert(String(prodData.gtin).includes(String(wrapper.vm.gtin13)));
                    });
                    it('Root.formData.gtin.value', () => {
                        expect(wrapper.vm.formData.gtin.value).to.equal(prodData.gtin);
                    });
                    it('Root.formData.package_level.value', () => {
                        expect(wrapper.vm.formData.package_level.value).to.equal(testPackageLevel);
                    });
                    it('Root.formData.package_type.value', () => {
                        expect(wrapper.vm.formData.package_type.value).to.equal(testPackageType);
                    });
                    it('Root.summaryContent', () => {
                        expect(wrapper.vm.summaryContent).to.equal(testSummary);
                    });
                    it('Root.id', () => {
                        expect(wrapper.vm.id).to.equal(prodData.id);
                    });
                    describe('form submit', () => {
                        let submitGtin;
                        let xhr;
                        let patchBody;
                        let patchGtin;

                        beforeEach(done => {
                            patchBody = undefined;
                            TokenService.redirect = sinon.spy();
                            server.respondWith('PATCH', /\/api\/v1\/products\/(\w+)\//, (xhr, gtin) => {
                                patchGtin = gtin;
                                patchBody = JSON.parse(xhr.requestBody);
                                xhr.respond(200, {
                                    'Content-Type': 'application/json'
                                }, JSON.stringify(_.cloneDeep({
                                    id: prodData.id
                                })));
                            });
                            wrapper.vm.submitForm();
                            done();
                        });
                        describe('values', () => {
                            _.each(_.omit(prodData, 'id', 'language'), (val, key) => {
                                it(key, () => {
                                    expect(prodData[key]).to.equal(patchBody[key]);
                                });
                            })
                        });
                        it('redirect', (done) => {
                            setTimeout(() => {
                                assert(TokenService.redirect.called);
                                done();
                            });
                        });
                        afterEach(() => {
                            delete require.cache[require.resolve('../../../src/common/services/TokenService')];
                        })
                    });
                    describe('API', () => {
                        _.each([
                            ['country_of_origin', 'countries'], ['target_market', 'targetMarketList'],
                            ['language', 'languageList'], ['package_type', 'packaging']
                        ], ([compKey, apiMockList]) => {
                            it(compKey, () => {
                                expect(wrapper.vm.formData[compKey].enum.length).to.equal(ApiMock[apiMockList].length);
                            })
                        })
                        it('barcodes', () => {
                            _.each(barcodesQueried, barcode => {
                                assert(wrapper.vm[barcode.toLowerCase() + 'Content'] === barcode + '_test')
                            });
                        });
                    });
                    describe('DeleteModal', () => {
                        let deleteGtin;
                        beforeEach(() => {
                            deleteGtin = undefined;
                            server.respondWith('DELETE', /\/api\/v1\/products\/(\w+)\//, (xhr, gtin) => {
                                deleteGtin = gtin;
                                xhr.respond(200, {
                                    'Content-Type': 'application/json'
                                }, JSON.stringify(_.cloneDeep({
                                    id: prodData.id
                                })));
                            });
                            wrapper.vm.$refs.deleteModal.open();
                            wrapper.vm.$refs.deleteModal.deleteProduct();
                        })
                        it('gtin', done => {
                            setTimeout(() => {
                                expect(wrapper.vm.gtin).to.equal(gtin);
                                done();
                            });
                        });
                        it('redirect', done => {
                            setTimeout(() => {
                                assert(TokenService.redirect.called);
                                done();
                            });
                        });
                    })
                });
            });
        });
    });
})
