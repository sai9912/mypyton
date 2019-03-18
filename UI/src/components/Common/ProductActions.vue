<template>
  <div class="product-actions">
    <div class="row">
      <router-link to="products/add" class="btn btn-primary">{{$t('Add product')}}</router-link>
    </div>
    <div class="row">
      <p style="margin-top: 10px;">{{$t('Allocate a new barcode from your Active Prefix')}}</p>
    </div>
    <br>
    <div class="row">
      <router-link to="products" class="btn btn-gs1ie-orange">{{$t('View Products')}}</router-link>
    </div>
    <div class="row">
      <p style="margin-top: 10px;">{{$t('View allocated numbers from your Active Prefix')}}</p>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'ProductActions'
  }
</script>

<style scoped>

</style>
