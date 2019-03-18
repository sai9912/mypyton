<template>
  <div class="panel panel-default">
    <div class="panel-heading">
      {{$t('Account Summary')}}
    </div>
    <div class="panel-body">
      <h4>{{$t('Symbol Credits')}}</h4>
      <p>{{$t('Points balance')}}:
        <strong>100</strong>
      </p>
      <p>
        <a href="http://www.gs1ie.org/Members-Area/My-Dashboard/Apply-for-Licences/">Purchase barcode image credits now</a>
      </p>
      <p>UUID: {{$store.state.auth.userData.member_organisation}}</p>
      <p>{{$t('Company Name')}}: <a href="#">{{$t('Blackwater Distillery Limited')}}</a></p>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'AccountSummary'
  }
</script>

<style scoped>

</style>
