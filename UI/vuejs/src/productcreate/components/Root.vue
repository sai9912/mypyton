<template>
    <router-view></router-view>
</template>

<script>

    export default {
        mounted() {
            this.$store.dispatch('ProductCreation/load');
        }
    };
</script>

<style lang="scss">
    .hide-empty:empty {
        display: none;
    }
</style>
