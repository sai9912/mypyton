import AccountSummary from './AccountSummary'
import {mount} from '@vue/test-utils'
import getTestEnv from '../../../../tests/unit/utils/localVue'
import Vuex from 'vuex'

describe('AccountSummary.vue', () => {
  const testEnv = getTestEnv()
  let store
  beforeEach(() => {
    store = new Vuex.Store({
      modules: {
        auth: {
          namespaced: true,
          state: {
            userData: {}
          },
          actions: {}
        }
      }
    })
  })

  it('should render correct contents', () => {
    const wrapper = mount(AccountSummary, {
      ...testEnv,
      store
    })

    expect(wrapper.find('.panel-heading').text())
      .to.equal(wrapper.vm.$t('Account Summary'))
  })
})
