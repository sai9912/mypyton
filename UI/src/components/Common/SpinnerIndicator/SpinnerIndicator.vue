<template>
  <div class="spinner-indicator" v-if="loading">
    <self-building-square-spinner
      :animation-duration="5000"
      :size="40"
      color="#f26334"
    ></self-building-square-spinner>
  </div>

</template>

<script>
  import {SelfBuildingSquareSpinner} from 'epic-spinners'
  export default {
    name: 'SpinnerIndicator',
    components: {SelfBuildingSquareSpinner},
    props: {
      loading: {
        type: Boolean,
        default: false
      }
    }
  }
</script>

<style scoped>
  .spinner-indicator {
    display: flex;
    align-items: center;
    width: 100%;
    justify-content: center;
    padding: 20px;
  }
</style>
