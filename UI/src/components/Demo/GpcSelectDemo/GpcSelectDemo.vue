<template>
  <div>

    <b-form-group
      label="GPC">
      <gpc-select  @input="selected = $event && $event.BrickCode"></gpc-select>
      <input type="hidden" name="category" :value="selected"/>
    </b-form-group>



    <div>
      Selected :{{selected}}
    </div>
  </div>
</template>

<script>
  export default {
    name: 'GpcSelectDemo',
    data() {
      return {
        selected: null
      }
    }
  }
</script>

<style scoped>

</style>
