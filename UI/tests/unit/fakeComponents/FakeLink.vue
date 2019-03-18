<template>
  <a :href="to">
    <slot/>
  </a>
</template>

<script>
  export default {
    name: 'fake-link',
    props: [
      'to'
    ]
  }
</script>

<style scoped>

</style>
