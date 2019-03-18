import VueI18n from 'vue-i18n'
import BootstrapVue from 'bootstrap-vue'
import {createLocalVue} from '@vue/test-utils'
import CommonComponents from '../../../src/components/Common/CommonInstall'

const getTestEnv = () => {
  const localVue = createLocalVue()
  localVue.use(BootstrapVue)
  localVue.use(VueI18n)
  localVue.use(CommonComponents)
  const i18n = new VueI18n({
    locale: 'en',
    messages: {
      en: require('./../../../src/locales/en.json'),
      de: require('./../../../src/locales/de.json'),
      fr: require('./../../../src/locales/fr.json'),
      sv: require('./../../../src/locales/sv.json')
    }
  })
  return {localVue, i18n}
}

export default getTestEnv
