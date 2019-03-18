<template>

  <div id="product_prefixes" class="tab-pane">
    <div class="row">
      <div class="col-md-12">
        <div class="panel panel-primary">
          <div class="panel-heading">
            {{$t('Your prefixes')}}
          </div>
          <div class="panel-body">
            <form method="POST">
              <p>
                {{
                $t('Click action button and select the desired action')
                }}.
              </p>
              <div class=panel-table-container>
                <table class="table table-condensed table-striped ">
                  <thead>
                  <th>{{$t('Prefix Description')}}</th>
                  <th>{{$t('Range')}}</th>
                  <th>{{$t('Next number')}}</th>
                  <th>{{$t('Products')}}</th>
                  <th></th>
                  </thead>
                  <tbody>

                  <tr v-for="item in items">
                    <td>
                      <a href="#" class="prefix-editable editable editable-click" data-type="text" data-pk="1282"
                         data-url="/prefixes/ajax/" data-title="Prefix Description">{{$t('Block of')}} {{item.capacity}}
                        GTINs</a>
                    </td>
                    <td>
                      <a href="/prefixes?prefix=1282">
                        <b>{{item.prefix}}</b><span style="color:#F26334">{{item.start}}</span>0 -
                        <b>{{item.prefix}}</b><span
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
                    <td>
                      <b-dropdown id="ddown-dropup" text="Actions" right variant="info">

                        <b-dropdown-item v-for="action in actions"
                                         :key="action.value"
                                         @click="doAction(action.value, item)">
                          {{$t(action.label)}}
                        </b-dropdown-item>


                      </b-dropdown>
                    </td>
                  </tr>

                  </tbody>
                </table>
                <spinner-indicator :loading="loading"></spinner-indicator>
              </div>


            </form>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
  import PrefixesService from '../../services/PrefixesService'

  export default {
    name: 'Prefixes',
    data: function () {
      return {
        loading: false,
        items: [],
        actions: [
          {
            value: 'new_gln',
            label: 'Enter a new product in selected range'
          },
          {
            value: 'set_gln',
            label: 'Set selected range as active and go to My Products'
          },
          {
            value: 'starting_gln',
            label: 'Set starting GTIN in selected range manually'
          },
          {
            value: 'first_available_gln',
            label: 'Set starting GTIN to first available number'
          },
          {
            value: 'export_available_gln',
            label: 'Export available GTINs in this range'
          }
        ]
      }
    },
    methods: {
      doAction(action, item) {
        switch (action) {
          case 'new_gln': {
            break
          }
          case 'set_gln': {
            this.$store.dispatch('prefixes/selectPrefix', item)
            this.$router.push('/products')
            break
          }
          case 'starting_gln': {
            break
          }
          case 'first_available_gln': {
            break
          }
          case 'export_available_gln': {
            break
          }
        }
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

<style scoped lang="scss">

  .table {
    tr {
      td {
        vertical-align: middle;
      }
    }
  }
</style>
