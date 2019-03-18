import Login from './Login'
import {mount} from '@vue/test-utils'
import getTestEnv from '../../../../tests/unit/utils/localVue'
import Vuex from 'vuex'
import Vuelidate from 'vuelidate'

describe('Login.vue', () => {
  const testEnv = getTestEnv()
  testEnv.localVue.use(Vuelidate)
  let actions
  let store
  let mockRouter

  beforeEach(() => {
    actions = {
      login: sinon.stub().resolves(),
      checkTerms: sinon.stub().resolves()
    }
    store = new Vuex.Store({
      modules: {
        auth: {
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
    const wrapper = mount(Login, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })

    const data = {
      email: 'test@test.com',
      password: '123456'
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    expect(actions.login).to.have.been.calledWith(sinon.match.any, {
      username: 'test@test.com',
      password: '123456'
    })
  })

  it('should not send incorrect data', () => {
    const wrapper = mount(Login, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      email: '',
      password: ''
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    expect(actions.login).to.have.callCount(0)
  })

  it('should redirect to dashboard', (done) => {
    const wrapper = mount(Login, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      email: 'test@test.com',
      password: '123456'
    }
    wrapper.setData(data)
    wrapper.vm.submit()
    setTimeout(() => {
      expect(mockRouter.push).to.have.been.calledWith('dashboard')
      done()
    }, 0)
  })

  it('should show required validation', (done) => {
    const wrapper = mount(Login, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      email: '',
      password: ''
    }
    wrapper.setData(data)
    wrapper.vm.submit()

    const message = wrapper.vm.$t('Field is required')
    setTimeout(() => {
      expect(wrapper.find('#email ~ div').text()).to.equal(message)
      expect(wrapper.find('#password ~ div').text()).to.equal(message)
      done()
    })
  })

  it('should show server validation', (done) => {
    const message = 'incorrect'
    actions = {
      login: sinon.stub().rejects({
        response: {
          data: {
            email: [message],
            password: [message]
          }
        }
      })
    }
    store = new Vuex.Store({
      modules: {
        auth: {
          namespaced: true,
          state: {},
          actions
        }
      }
    })

    const wrapper = mount(Login, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      email: 'test@test.com',
      password: '123456'
    }
    wrapper.setData(data)
    wrapper.vm.submit()

    setTimeout(() => {
      expect(wrapper.find('#email ~ div').text()).to.equal(message)
      expect(wrapper.find('#password ~ div').text()).to.equal(message)
      done()
    })
  })

  it('should show email format validation', (done) => {
    const wrapper = mount(Login, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    const data = {
      email: 'test'
    }
    wrapper.setData(data)
    wrapper.vm.submit()

    const message = wrapper.vm.$t('Email is incorrect')
    setTimeout(() => {
      expect(wrapper.find('#email ~ div').text()).to.equal(message)
      done()
    })
  })

  it('should show message for logged user', () => {
    const userData = {
      email: 'email'
    }

    store = new Vuex.Store({
      modules: {
        auth: {
          namespaced: true,
          state: {
            isAuth: true,
            userData
          },
          actions
        }
      }
    })
    const wrapper = mount(Login, {
      ...testEnv,
      store,
      mocks: {
        $router: mockRouter
      }
    })
    expect(wrapper.find('.auth-message .user-email').text()).to.equal(userData.email)
  })
})
