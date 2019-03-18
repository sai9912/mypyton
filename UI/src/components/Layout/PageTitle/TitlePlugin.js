import * as _ from 'lodash'

function install(Vue, options) {
  function getPageTitle(route) {
    const matched = route.matched
    return _.last(matched.map((route) => {
      return route.meta && route.meta.pageTitle
    }))
  }

  Object.defineProperty(Vue.prototype, '$pageTitle', {
    get: function () {
      return getPageTitle(this.$route)
    }
  })

  Vue.directive('title', {
    inserted(el, binding, vnode) {
      document.title = vnode.context.$t('GS1 Ireland Dashboard') + ': ' + vnode.context.$t(getPageTitle(vnode.context.$route))
    },
    update(el, binding, vnode) {
      document.title = vnode.context.$t('GS1 Ireland Dashboard') + ': ' + vnode.context.$t(getPageTitle(vnode.context.$route))
    }
  })
}

export default {
  install: install
}
