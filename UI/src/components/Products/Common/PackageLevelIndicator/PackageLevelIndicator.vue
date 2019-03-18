<template>
  <div>
    <div v-if="packageLevel ===  40">
      <img src="./wizard/shipper.png" alt="Display shipper"
           class="package-level">
    </div>
    <div v-else-if="packageLevel === 70">
      <img src="./wizard/pos.png" alt="Each" class="package-level">
    </div>
    <div v-else-if="packageLevel === 60">
      <img src="./wizard/pack.png" alt="Pack" class="package-level">
    </div>
    <div v-else-if="packageLevel === 50">
      <img src="./wizard/case.png" alt="Case"  class="package-level">
    </div>
    <div v-else>
      <img src="./wizard/pallet.png" alt="Pallet" class="package-level">
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
    }
  }
</script>

<style scoped>

  .package-level{
    width: auto;
    height: auto;
    max-width: 20px;
    max-height: 20px;
  }
</style>
