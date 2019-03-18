import AcceptTerms from './AcceptTerms'
import {mount} from '@vue/test-utils'
import getTestEnv from '../../../../tests/unit/utils/localVue'
import Vuex from 'vuex'
import Vuelidate from 'vuelidate'
import moment from 'moment'
import FakeLink from '../../../../tests/unit/fakeComponents/FakeLink'

describe('AcceptTerms.vue', () => {
  const testEnv = getTestEnv()
  testEnv.localVue.use(Vuelidate)
  let actions
  let store
  let mockRouter

  beforeEach(() => {
    actions = {
      acceptTerms: sinon.stub().resolves()
    }
    store = new Vuex.Store({
      modules: {
        auth: {
          namespaced: true,
          state: {
            terms: {
              date_terms: moment()
            }
          },
          actions
        }
      }
    })
    mockRouter = {
      push: sinon.spy()
    }
  })

  it('should send correct data', () => {
    const wrapper = mount(AcceptTerms, {
      ...testEnv,
      store,
      stubs: {
        'router-link': FakeLink
      },
      mocks: {
        $router: mockRouter
      }
    })
    wrapper.setData({
      agree: true
    })
    wrapper.vm.submit()
    expect(actions.acceptTerms).to.have.callCount(1)
  })

  it('should not send incorrect data', () => {
    const wrapper = mount(AcceptTerms, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    wrapper.vm.submit()
    expect(actions.acceptTerms).to.have.callCount(0)
  })

  it('should redirect to dashboard', (done) => {
    const wrapper = mount(AcceptTerms, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    wrapper.setData({
      agree: true
    })
    wrapper.vm.submit()
    setTimeout(() => {
      expect(mockRouter.push).to.have.been.calledWith('dashboard')
      done()
    }, 0)
  })

  it('should show required validation', (done) => {
    const wrapper = mount(AcceptTerms, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    wrapper.vm.submit()
    setTimeout(() => {
      expect(wrapper.vm.$v.agree.$error).to.equal(true)
      done()
    })
  })
})
