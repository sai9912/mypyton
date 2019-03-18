import PageTitle from './PageTitle'
import {mount} from '@vue/test-utils'
import getTestEnv from '../../../../tests/unit/utils/localVue'
import TitlePlugin from './TitlePlugin'

describe('PageTitle.vue', () => {
  const testEnv = getTestEnv()
  testEnv.localVue.use(TitlePlugin)
  const matched = [
    {
      meta: {
        pageTitle: 'Dashboard'
      }
    }
  ]
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

  it('should show Page Title', () => {
    const wrapper = mount(PageTitle, {
      ...testEnv
    })
    expect(wrapper.find('h2').text())
      .to.equal(matched[0].meta.pageTitle)
  })

  it('should show last Page Title', () => {
    matched.push(
      {
        meta: {
          pageTitle: 'My Products'
        }
      }
    )
    const wrapper = mount(PageTitle, {
      ...testEnv
    })
    expect(wrapper.find('h2').text())
      .to.equal(matched[1].meta.pageTitle)
  })
})
