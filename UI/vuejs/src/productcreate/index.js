
import Root from './components/Root';
import store from './store/index';
import router from './router/';

export default {
    el: document.querySelector('.ProductCreateApp'),
    render: h => h(Root),
    store,
    router
};