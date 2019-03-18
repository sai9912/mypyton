<template>
    <div>
        <div class="site" v-if="!isPending">
            <layout-header/>
            <breadcrumbs default-state="dashboard" default-state-name="Home"/>
            <messages/>

            <div class="container container--content">

                <div class="site-main row" :class="{'site-main--small':!showNavMenu}">


                    <nav-menu v-if="showNavMenu"/>
                    <div class="site-content col">
                        <page-title/>
                        <div class="site-content-padder">
                            <router-view/>
                        </div>
                        <div class='clearfix'></div>
                    </div>


                </div>


            </div>

            <layout-footer/>
        </div>
        <div v-else>
            Please Wait
        </div>

    </div>

</template>

<script>
    import LayoutHeader from './LayoutHeader/LayoutHeader'
    import LayoutFooter from './LayoutFooter/LayoutFooter'
    import Breadcrumbs from './Breadcrumbs/Breadcrumbs'
    import Messages from './Messages/Messages'
    import NavMenu from './NavMenu/NavMenu'
    import PageTitle from './PageTitle/PageTitle'

    export default {
        name: 'layout',
        components: {
            LayoutHeader,
            Breadcrumbs,
            Messages,
            NavMenu,
            PageTitle,
            LayoutFooter
        },
        props: {
            showNavMenu: {
                type: Boolean
            }
        },
        computed: {
            isPending() {
                return this.$store.state.auth.isAuth && this.$store.state.auth.loginDjangoPending
            }
        }
    }
</script>

<style scoped lang="scss">

    .site {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .site-main {
        position: relative;
    }

    .site-main--small {
        width: 600px;
        margin-left: auto;
        margin-right: auto;

        .site-content {
            min-height: 0px;
        }
    }

    .container--content {
        flex: 1 0 auto;

    }

    .site-content {
        padding: 0px;
        margin-bottom: 10px;
    }

    .site-content-padder {
        padding: 20px 40px;
    }
</style>
