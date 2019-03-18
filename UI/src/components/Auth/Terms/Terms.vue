<template>

  <div class="terms">
    <div v-if="!loading && this.$store.state.auth.terms">
      <h4>Last update:{{versionData}}</h4>
      <p>
        <textarea cols="80" rows="20" name="myname" :value="version" readonly></textarea>
      </p>
      <p>
      </p>
      <h4>Last update: {{versionCloudDate}}</h4>
      <textarea cols="80" rows="20" name="myname" :value="versionCloud" readonly> </textarea>
      <p></p>


    </div>
    <spinner-indicator :loading="loading" class="spinner"></spinner-indicator>
  </div>
</template>

<script>
  import moment from 'moment'

  export default {
    name: 'Terms',
    data() {
      return {
        loading: false
      }
    },
    computed: {
      versionData() {
        return moment(this.$store.state.auth.terms.date_terms).format('L')
      },
      versionCloudDate() {
        return moment(this.$store.state.auth.terms.date_terms_cloud).format('L')
      },
      version() {
        return this.$store.state.auth.terms.terms
      },
      versionCloud() {
        return this.$store.state.auth.terms.terms_cloud
      }
    },
    async mounted() {
      this.loading = true
      try {
        await this.$store.dispatch('auth/getTerms')
      } catch (ex) {
      }
      this.loading = false
    }
  }
</script>

<style scoped>
  .terms {
    max-width: 600px;
    margin: 0 auto;
    min-height: 200px;
  }

  .spinner {
    margin-top: 100px;
  }

  textarea {
    width: 100%;
  }
</style>
