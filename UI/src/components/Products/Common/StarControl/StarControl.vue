<template>
  <span class="star-control" @click="change()">
    <i class="fas fa-star selected" v-if="value"></i>
    <i class="far fa-star" v-else></i>
  </span>

</template>

<script>
  export default {
    name: 'StarControl',
    props: {
      value: {
        required: true
      },
      readonly: {
        required: false,
        default: false
      }
    },
    methods: {
      change() {
        if (!this.readonly) {
          this.$emit('input', !this.value)
        }
      }
    }
  }
</script>

<style scoped>
  .star-control {
    font-size: 16px;
    cursor: pointer;
  }
  .selected
  {
    color: #ffda76;
  }
</style>
