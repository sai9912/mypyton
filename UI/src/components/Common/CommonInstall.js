import VueLadda from './Form/VueLaddaButton/VueLaddaButton'
import SpinnerIndicator from './SpinnerIndicator/SpinnerIndicator'
import GpcSelect from './Form/GpcSelect/GpcSelect'

const installer = {
  install(Vue, options) {
    Vue.component('vue-ladda', VueLadda)
    Vue.component('spinner-indicator', SpinnerIndicator)
    Vue.component('gpc-select', GpcSelect)
  }
}
export default installer
