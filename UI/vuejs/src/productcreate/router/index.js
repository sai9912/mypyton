import Vue from 'vue';
import VueRouter from 'vue-router';
import PackagingLevelStep from '../components/PackagingLevelStep.vue';
import PackagingTypeStep from '../components/PackagingTypeStep.vue';
import PackagingDetailsStep from '../components/PackagingDetailsStep.vue';
import Summary from '../components/Summary.vue';

Vue.use(VueRouter);

const router = new VueRouter({
    linkActiveClass: 'active',
    mode: 'hash',
    base: '/',
    routes: [
        {
            path: '/',
            component: PackagingLevelStep
        },
        {
            path: '/packagingType',
            component: PackagingTypeStep
        },
        {
            path: '/details',
            component: PackagingDetailsStep
        },
        {
            path: '/summary',
            component: Summary
        }
    ],
    scrollBehavior() {
        return {x: 0, y: 0}
    }
});

router.beforeEach((to, from, next) => {
    next();
});

export default router;
