<template>
    <div>


        <list-products-s-t :user-data-outer="$store.state.auth.userData" :is-spa="true">

        </list-products-s-t>
    </div>


</template>

<script>
    import PackageLevelIndicator from '../Common/PackageLevelIndicator/PackageLevelIndicator'
    import StarControl from '../Common/StarControl/StarControl'
    import * as _ from 'lodash'

    import ListProductsST from '../../../../vuejs/src/productList/ListProducts/ListProducts'

    export default {
        name: 'list-products',
        components: {
            PackageLevelIndicator,
            ListProductsST,
            StarControl
        },
        data() {
            return {}
        },
        computed: {},
        watch: {},
        methods: {},
        mounted() {

        }
    }
</script>

<style scoped lang="scss">


</style>
