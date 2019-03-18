import Vue from 'vue';
import Raven from 'raven-js';
import RavenVue from 'raven-js/plugins/vue';

if(process.env.RAVEN_VAR ==='on')
{
    console.log('r start');
    Raven
        .config('https://683339d8744a40028f91c131e4b046f1@sentry.io/1226302', {
            ignoreUrls: ['localhost', '127.0.0.1']
        })
        .addPlugin(RavenVue, Vue)
        .install();
}

