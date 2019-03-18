<template>
    <div>
        <div v-if="packageLevel ===  40">
            <img :src="'/static/products/site/wizard/shipper.png'" :alt="gettext('Display shipper')"
                 :title="gettext('Display shipper')"
                 class="package-level">
        </div>
        <div v-else-if="packageLevel === 70">
            <img :src="'/static/products/site/wizard/pos.png'" :alt="gettext('Base Unit')" :title="gettext('Base Unit')"
                 class="package-level">
        </div>
        <div v-else-if="packageLevel === 60">
            <img :src="'/static/products/site/wizard/pack.png'" :alt="gettext('Pack')" :title="gettext('Pack')"
                 class="package-level">
        </div>
        <div v-else-if="packageLevel === 50">
            <img :src="'/static/products/site/wizard/case.png'" :alt="gettext('Case')" :title="gettext('Case')"
                 class="package-level">
        </div>
        <div v-else>
            <img :src="'/static/products/site/wizard/pallet.png'" :alt="gettext('Pallet')" :title="gettext('Pallet')"
                 class="package-level">
        </div>
    </div>
</template>

<script>
    export default {
        name: 'PackageLevelIndicator',
        props: {
            packageLevel: {
                required: true
            }
        },
        methods: {
            gettext(val) {
                return gettext(val)
            }
        }
    }
</script>

<style scoped>

    .package-level {
        width: auto;
        height: auto;
        max-width: 20px;
        max-height: 20px;
    }
</style>
