import router from './index'
import store from '../store'

router.beforeEach((to, from, next) => {
  if (to.matched.some((item) => item.meta.onlyAuth)) {
    const isAuth = store.state.auth.isAuth
    if (!isAuth) {
      next('/login')
    } else if (store.state.auth.needAcceptTerms && to.path !== '/accept-terms') {
      next('/accept-terms')
    } else {
      next()
    }
  } else {
    next()
  }
})
