import Breadcrumbs from './Breadcrumbs'
import {mount} from '@vue/test-utils'
import getTestEnv from '../../../../tests/unit/utils/localVue'
import FakeLink from '../../../../tests/unit/fakeComponents/FakeLink'
import VueBreadcrumbs from 'vue-breadcrumbs'

describe('Breadcrumbs.vue', () => {
  const testEnv = getTestEnv()
  testEnv.localVue.use(VueBreadcrumbs)
  const matched = []
  testEnv.localVue.use(
    {
      install: function install(Vue, options) {
        Object.defineProperty(Vue.prototype, '$route', {
          get: function () {
            return {
              matched
            }
          }
        })
      }
    }
  )

  it('should render default state', () => {
    const wrapper = mount(Breadcrumbs, {
      ...testEnv,
      stubs: {
        'router-link': FakeLink
      },
      propsData: {
        defaultState: 'dashboard',
        defaultStateName: 'Home'
      }
    })
    expect(wrapper.findAll('.breadcrumb-item > *').at(0).text())
      .to.equal('Home')
  })

  it('should render breadcrumbs', () => {
    matched.push(
      {
        meta: {
          breadcrumb: 'Dashboard'
        }
      }
    )
    const wrapper = mount(Breadcrumbs, {
      ...testEnv,
      stubs: {
        'router-link': FakeLink
      },
      propsData: {
        defaultState: 'dashboard',
        defaultStateName: 'Home'
      }
    })

    expect(wrapper.findAll('.breadcrumb-item > *').at(1).text())
      .to.equal(matched[0].meta.breadcrumb)
  })
})
