<template>
    <div>
        Please Wait
    </div>
</template>

<script>
    export default {
        name: "AppWait",
        computed: {
            isPending () {
                return this.$store.state.auth.loginDjangoPending
            }
        },
        mounted() {
            if (!this.isPending) {
                this.$router.push('/dashboard')
            }
        },
        watch: {
            isPending(val) {
                if (!val) {
                    this.$router.push('/dashboard')
                }
            }
        }
    }
</script>

<style scoped>

</style>
