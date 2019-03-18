<template>
  <div id="prefix-info" class="active-prefixes well well-sm">
    <h4>{{$t('Active Prefix')}}</h4>
    <ul class="list-unstyled" v-if="!$store.state.prefixes.loading && $store.state.prefixes.activePrefix">
      <li>GCP: <b>{{$store.state.prefixes.activePrefix.prefix}}</b></li>
      <li><b>Products:</b></li>
      <li>{{ $t('Allocated') }}: <b>{{$store.state.prefixes.activePrefix.gtins_allocated}}</b></li>
      <li>{{ $t('Available') }}: <b>{{$store.state.prefixes.activePrefix.gtins_available}}</b></li>
      <li v-if="false"><b>Locations:</b></li>
      <li v-if="false">{{ $t('Allocated') }}: <b>{{$store.state.prefixes.locationAllocated}}</b></li>
      <li v-if="false"> {{ $t('Available') }}: <b> {{$store.state.prefixes.locationAvailable}} </b></li>
    </ul>
    <spinner-indicator :loading="$store.state.prefixes.loading"></spinner-indicator>
  </div>
</template>

<script>
  export default {
    name: 'ActivePrefix',
    data() {
      return {}
    },
    computed: {},
    mounted() {
      this.$store.dispatch('prefixes/loadPrefixes')
    }
  }
</script>

<style scoped>

</style>
