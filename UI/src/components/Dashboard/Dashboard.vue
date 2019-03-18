<template>
    <div>
        <st-dashboard :user-data="$store.state.auth.userData">

        </st-dashboard>
        <div class="row" v-if="false">

            <div class="col-md-6">
                <AccountSummary></AccountSummary>
            </div>
            <div class="col-md-6">
                <ProductActions></ProductActions>
            </div>
            <div class="col-md-12">
                <CompanyPrefixes></CompanyPrefixes>
            </div>
        </div>
    </div>


</template>

<script>
    import AccountSummary from '../Common/AccountSummary/AccountSummary'
    import ProductActions from '../Common/ProductActions'
    import CompanyPrefixes from '../Common/CompanyPrefixes'
    import StDashboard from './../../../vuejs/src/dashboard/components/Root';

    export default {
        name: 'Dashboard',
        components: {
            AccountSummary,
            ProductActions,
            CompanyPrefixes,
            StDashboard
        },
        data: function () {
            return {}
        }
    }
</script>

<style scoped>

</style>
