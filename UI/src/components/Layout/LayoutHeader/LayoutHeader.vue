<template>
    <header class="site-header">
        <nav class="navbar navbar-expand-md p-0" role="navigation">
            <div class="container my-0"><a class="navbar-brand mr-0" href="/"> <img
                    src="/static/site/img/gs1ie-logo.png"
                    class="d-inline-block align-top" alt=""/>
            </a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav ml-auto">
                        <li class="nav-item"><a href="/" class="nav-link">{{ $t('Home') }}</a></li>
                        <li class="nav-item"><a href="http://gs1ie-help.barcoderobot.com/"
                                                class="nav-link">{{ $t('Support') }}</a>
                        </li>
                        <li class=" nav-item">
                            <a href="http://www.gs1ie.org/Members-Area/My-Dashboard" class="nav-link">
                                {{ $t('GS1 Ireland Dashboard') }}
                            </a>
                        </li>
                        <li class=" nav-item" v-if="!$store.state.auth.isAuth">
                            <router-link to="login" class="nav-link"> {{ $t('Sign In') }}</router-link>
                        </li>

                        <li class=" nav-item">
                            <localization :language="language"/>
                        </li>
                        <template v-if="$store.state.auth.isAuth">
                            <li class=" nav-item mt-2 ml-3">
                                <span class="nav-user-info_label">{{ $t('Company name') }}:</span>
                                {{$store.state.auth.userData.company_organisation }}<br/>
                                <span class="nav-user-info_label">{{ $t('User') }}:</span><a
                                    :href="'mailto:'+$store.state.auth.userData.email"
                                    style="padding:0px; display:inline;">{{ $store.state.auth.userData.email }}</a>

                            </li>

                            <li class=" nav-item mt-2 ml-3">
                                <router-link to="login" class="nav-link" @click.native="logout()"
                                             v-if="!$store.state.auth.isImpersionate">
                                    {{ $t('Sign Out') }}
                                </router-link>

                                <a href="/impersonate/stop/" class="btn btn-warning"
                                   v-if="$store.state.auth.isImpersionate">
                                    {{ $t('Stop Impersionate') }}
                                </a>

                            </li>
                        </template>


                    </ul>
                </div>
            </div>
        </nav>
    </header>
</template>
<script>
    import Localization from './Localization/Localization'

    export default {
        name: 'LayoutHeader',
        components: {
            Localization
        },
        data() {
            return {
                languages: []
            }
        },
        computed: {
            language() {
                if (this.$store.state.auth.isAuth) {
                    return this.$store.state.auth.userData.language;
                } else {
                    return 'en';
                }
            }
        },
        methods: {
            logout() {
                this.$store.dispatch('auth/logout')
            }
        }
    }
</script>

<style scoped>
    .select-language {
        padding: 10px;
    }

    .select-language .btn-link {
        color: #002c6c;
    }

</style>
<style>
    .select-language .btn-link {
        color: #002c6c;
    }
</style>
