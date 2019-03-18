import AccountApi from './AccountApi'
import {mount} from '@vue/test-utils'
import getTestEnv from '../../../../tests/unit/utils/localVue'
import Vuex from 'vuex'
import Vuelidate from 'vuelidate'

describe('AccountApi.vue', () => {
  const testEnv = getTestEnv()
  testEnv.localVue.use(Vuelidate)
  let actions
  let store
  let mockRouter

  beforeEach(() => {
    actions = {
      register: sinon.stub().resolves()
    }
    store = new Vuex.Store({
      modules: {
        accountApi: {
          namespaced: true,
          state: {},
          actions
        }
      }
    })
    mockRouter = {
      push: sinon.spy()
    }
  })

  it('should send correct data', () => {
    const wrapper = mount(AccountApi, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })

    const data = {
      uuid: 'test',
      email: 'test@test.com',
      company_prefix: 'test',
      company_name: 'test',
      credits: 'test',
      txn_ref: 'test',
      member_organisation: 'test'
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    expect(actions.register).to.have.been.calledWith(sinon.match.any, data)
  })

  it('should not send incorrect data', () => {
    const wrapper = mount(AccountApi, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      uuid: '',
      email: '',
      company_prefix: '',
      company_name: '',
      credits: '',
      txn_ref: '',
      member_organisation: ''
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    expect(actions.register).to.have.callCount(0)
  })

  it('should redirect to dashboard', (done) => {
    const wrapper = mount(AccountApi, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      uuid: 'test',
      email: 'test@test.com',
      company_prefix: 'test',
      company_name: 'test',
      credits: 'test',
      txn_ref: 'test',
      member_organisation: 'test'
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    setTimeout(() => {
      expect(mockRouter.push).to.have.been.calledWith('dashboard')
      done()
    }, 0)
  })

  it('should show required validation', (done) => {
    const wrapper = mount(AccountApi, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      uuid: '',
      email: '',
      company_prefix: '',
      company_name: '',
      credits: '',
      txn_ref: '',
      member_organisation: ''
    }
    wrapper.setData(data)
    wrapper.vm.submit()

    const message = wrapper.vm.$t('Field is required')
    setTimeout(() => {
      expect(wrapper.find('#uuid ~ div').text()).to.equal(message)
      expect(wrapper.find('#email ~ div').text()).to.equal(message)
      expect(wrapper.find('#company_prefix ~ div').text()).to.equal(message)
      done()
    })
  })

  it('should show server validation', (done) => {
    const message = 'incorrect prefix'
    actions = {
      register: sinon.stub().rejects({
        response: {
          data: {
            uuid: [message],
            email: [message],
            company_prefix: [message],
            company_name: [message],
            credits: [message],
            txn_ref: [message]
          }
        }
      })
    }
    store = new Vuex.Store({
      modules: {
        accountApi: {
          namespaced: true,
          state: {},
          actions
        }
      }
    })

    const wrapper = mount(AccountApi, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      uuid: 'test',
      email: 'test@test.com',
      company_prefix: 'test',
      company_name: 'test',
      credits: 'test',
      txn_ref: 'test',
      member_organisation: 'test'
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    wrapper.vm.$v.$touch()
    setTimeout(() => {
      expect(wrapper.find('#uuid ~ div').text()).to.equal(message)
      expect(wrapper.find('#email ~ div').text()).to.equal(message)
      expect(wrapper.find('#company_prefix ~ div').text()).to.equal(message)
      expect(wrapper.find('#company_name ~ div').text()).to.equal(message)
      expect(wrapper.find('#credits ~ div').text()).to.equal(message)
      expect(wrapper.find('#txn_ref ~ div').text()).to.equal(message)
      done()
    })
  })

  it('should show email format validation', (done) => {
    const wrapper = mount(AccountApi, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      uuid: '',
      email: 'test',
      company_prefix: '',
      company_name: '',
      credits: '',
      txn_ref: '',
      member_organisation: ''
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    const message = wrapper.vm.$t('Email is incorrect')
    setTimeout(() => {
      expect(wrapper.find('#email ~ div').text()).to.equal(message)
      done()
    })
  })
})
