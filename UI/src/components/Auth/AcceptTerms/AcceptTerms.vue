<template>
  <div class="accept-terms">


    <i18n path="Auth.YouMustAgreeTerms" tag="p">
      <router-link place="terms"
         to="/terms"
         style="text-decoration: underline;">{{$t('Auth.TermsAndConditions')}}</router-link>
    </i18n>

    <form @submit.prevent="submit"
          name="loginForm"
          novalidate="true"
          class="terms-form"
    >

      <div class="terms-group">
        <b-form-checkbox id="agree"
                         v-model="agree"
                         @change="$v.agree.$touch()"
                         :unchecked-value="false">
          {{$t('Auth.IAgreeWithTerm')}}:<br/>
          {{$t('Auth.Version')}} {{version}}.
        </b-form-checkbox>

        <p class="text-danger"
           v-if="this.$v.agree.$error">
          {{$t('Auth.AcceptTermsValidation')}}
        </p>

        <div v-if="serverErrors && serverErrors.non_field_errors">
          <p class="text-danger"
             v-for="item in serverErrors.non_field_errors">
            {{item}}
          </p>
        </div>
      </div>

      <vue-ladda button-type="submit"
                 class="pull-right"
                 :loading="loading"
                 :error="serverErrors"
                 data-style="expand-right">
        {{$t('Submit')}}
      </vue-ladda>
    </form>
  </div>
</template>

<script>
  import {required} from 'vuelidate/lib/validators'
  import moment from 'moment'

  export default {
    name: 'AcceptTerms',
    data() {
      return {
        agree: false,
        serverErrors: null,
        loading: false,
        terms_version: ''
      }
    },
    computed: {
      version() {
        return moment(this.$store.state.auth.terms.date_terms).format('L')
      }
    },
    methods: {
      submit() {
        if (!this.$v.$invalid) {
          this.loading = true
          this.$store.dispatch('auth/acceptTerms').then(() => {
            this.$router.push('dashboard')
          }).catch(err => {
            this.serverErrors = err.response.data
            this.$v.$touch()
          }).finally(() => {
            this.loading = false
          })
        } else {
          this.$v.$touch()
        }
      }
    },
    mounted() {
    },
    validations: {
      agree: {
        required
      }
    }
  }
</script>

<style scoped>
  .accept-terms {
    max-width: 600px;
    margin: 0 auto;
  }

  .terms-form {

    display: flex;
    justify-content: space-between;
  }

</style>
