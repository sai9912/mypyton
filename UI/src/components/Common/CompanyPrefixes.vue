<template>
  <div class="panel panel-primary">
    <div class="panel-heading">
      {{$t('Global Company Prefixes and GTIN Ranges')}}
    </div>
    <div class="panel-body panel-table-container">
      <table class="table table-condensed table-striped">
        <thead>
        <tr>
          <th>{{$t('Prefix Description')}}</th>
          <th>{{$t('Range')}}</th>
          <th>{{$t('Next number')}}</th>
          <th>{{$t('Products')}}</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="item in items">
          <td>
            <a href="#" class="prefix-editable editable editable-click" data-type="text" data-pk="1282"
               data-url="/prefixes/ajax/" data-title="Prefix Description">{{$t('Block of')}} {{item.capacity}} GTINs</a>
          </td>
          <td>
            <a href="/prefixes?prefix=1282">
              <b>{{item.prefix}}</b><span style="color:#F26334">{{item.start}}</span>0 - <b>{{item.prefix}}</b><span
              style="color:#F26334">{{item.end}}</span>9
            </a>
          </td>
          <td>
            <b>{{item.prefix}}</b><span style="color:#F26334">{{item.start}}</span>0
          </td>
          <td>
            <a href="/products?prefix=539153224">4
              {{$t('Products')}}</a>
          </td>
        </tr>
        </tbody>
      </table>

      <spinner-indicator :loading="loading"></spinner-indicator>
    </div>
  </div>
</template>

<script>
  import PrefixesService from '../../services/PrefixesService'

export default {
    name: 'CompanyPrefixes',
    data() {
      return {
        loading: false,
        items: []
      }
    },
    mounted() {
      this.loading = true
      PrefixesService.getList().then((result) => {
        this.items = result
        for (const item of this.items) {
          item.capacity = Math.pow(10, 12 - item.prefix.length)
          item.start = '0'.repeat(12 - item.prefix.length)
          item.end = '9'.repeat(12 - item.prefix.length)
        }
      }).finally(() => {
        this.loading = false
      })
    }
  }
</script>

<style scoped>

</style>
