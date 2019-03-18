<template>
  <div class="container breadcrumbs">
    <div class="site-breadcrumbs row mx-0">
      <b-breadcrumb :items="breadcrumbs"></b-breadcrumb>
    </div>

  </div>

</template>

<script>
  export default {
    name: 'breadcrumbs',
    props: [
      'defaultState',
      'defaultStateName'
    ],
    computed: {
      breadcrumbs() {
        return [
          {
            text: this.$t(this.defaultStateName),
            to: this.defaultState
          },
          ...this.$breadcrumbs.map((crumb) => {
            return {
              to: this.linkProp(crumb),
              text: this.$t(crumb.meta.breadcrumb)
            }
          })
        ]
      }
    },
    methods: {
      linkProp: function (crumb) {
        return {
          name: crumb.name,
          params: this.$route.params
        }
      }
    }
  }
</script>

<style scoped>
  .breadcrumb {
    width: 100%;
  }

  .breadcrumb-item + .breadcrumb-item::before {
    color: #ccc;
  }
</style>
