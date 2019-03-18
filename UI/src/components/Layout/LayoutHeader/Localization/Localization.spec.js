import Localization from './Localization'
import {shallow, mount} from '@vue/test-utils'
import getTestEnv from '../../../../../tests/unit/utils/localVue'

describe('Localization.vue', () => {
  const testEnv = getTestEnv()

  it('should render correct count of language', () => {
    const wrapper = shallow(Localization, {
      ...testEnv
    })
    expect(wrapper.vm.languages.length)
      .to.equal(Object.keys(testEnv.i18n.messages).length)
  })

  it('should update language by select', () => {
    const wrapper = mount(Localization, {
      ...testEnv
    })
    const lastIndex = Object.keys(testEnv.i18n.messages).length - 1
    const lastLang = Object.keys(testEnv.i18n.messages)[lastIndex]

    const select = wrapper.find('.lang-select').element
    select.value = lastLang
    select.dispatchEvent(new Event('change'))

    expect(testEnv.i18n.locale)
      .to.equal(lastLang)
  })
})
