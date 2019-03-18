<template>

  <div>
    <v-select label="name"
              :filterable="false"
              :options="options"
              :value="value"
              @input="onSelect($event)"
              @search="onSearch">
      <template slot="no-options">
        <span v-if="!searchStr">
           {{$t('Please enter at least 3 characters')}}
        </span>
        <span v-if="searchStr">
             {{$t('Results not found')}}
        </span>

      </template>
      <template slot="option" slot-scope="option">
        {{option.Brick}} (<strong>{{option.BrickCode}}</strong>)
      </template>
      <template slot="selected-option" slot-scope="option">
        <span v-if="option.Brick">{{option.Brick}} (<strong>{{option.BrickCode}}</strong>)</span>
        <span v-else>{{option.BrickCode}}</span>
      </template>
    </v-select>
  </div>

</template>

<script>
  import vSelect from 'vue-select'
  import _ from 'lodash'
  import GPCServices from './../../../../services/GPCServices'
  import FormConstants from '../FormConstants'

  export default {
    name: 'GpcSelect',
    components: {
      vSelect
    },
    props: {
      value: {
        type: Object
      }
    },
    data() {
      return {
        selected: null,
        options: [],
        searchStr: null
      }
    },
    methods: {
      onSelect($event) {
        this.$emit('input', $event)
      },
      onSearch(search, loading) {
        if (search.length > 2) {
          loading(true)
          this.searchStr = search
          this.search(loading, search, this)
        } else {
          this.searchStr = null
          this.options = []
        }
      },
      search: _.debounce((loading, search, vm) => {
        const param = {}
        const isNum = /^\d+$/.test(search)
        if (isNum) {
          param.brick_code = search
        } else {
          param.brick = search
        }
        GPCServices.getList(param).then(res => {
          vm.options = res
        }).finally(() => {
          loading(false)
        })
      }, FormConstants.SEARCH_TIMEOUT)
    }
  }
</script>

<style>


</style>
