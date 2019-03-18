<template>
  <div>

    <i18n v-if="$store.state.auth.isAuth" path="Auth.AlreadyLogin" tag="p" class="auth-message">
      <strong place="email" class="user-email">{{$store.state.auth.userData.email}}</strong>
      <a place="action" href="" @click.prevent="logout()">{{$t('Auth.Log-out')}}</a>
    </i18n>


    <form @submit.prevent="submit" name="loginForm" novalidate="true">

      <b-form-group
        label="Email address"
        label-for="email"
        :invalid-feedback="invalidFeedbackEmail()"
        :state="$v.email.$error?false:null"
      >
        <b-form-input
          id="email"
          name="email"
          :state="$v.email.$error?false:null"
          @change="touch('email')"
          v-model.trim="email">
        </b-form-input>
      </b-form-group>


      <b-form-group
        label="Password"
        label-for="password"
        :invalid-feedback="invalidFeedbackPassword()"
        :state="$v.password.$error?false:null"
      >
        <b-form-input
          id="password"
          name="password"
          type="password"
          :state="$v.password.$error?false:null"
          @change="touch('password')"
          v-model.trim="password">
        </b-form-input>
      </b-form-group>
      <div v-if="serverErrors && serverErrors.non_field_errors">
        <p class="text-danger" v-for="item in serverErrors.non_field_errors">{{item}}</p>
      </div>
      <vue-ladda button-type="submit" :loading="loading" :error="serverErrors" data-style="expand-right">Login
      </vue-ladda>
    </form>
  </div>
</template>

<script>
  import {required, email} from 'vuelidate/lib/validators'
  import {serverValidation} from '../../../helpers/vuelidate'

  export default {
    name: 'Login',
    data() {
      return {
        email: '',
        password: '',
        serverErrors: null,
        loading: false
      }
    },
    computed: {},
    methods: {
      invalidFeedbackEmail() {
        if (!this.$v.email.required) {
          return this.$t('Field is required')
        } else if (!this.$v.email.email) {
          return 'Email is incorrect'
        } else if (this.serverErrors && this.serverErrors.email) {
          return this.serverErrors.email[0]
        } else {
          return null
        }
      },
      invalidFeedbackPassword() {
        if (!this.$v.password.required) {
          return this.$t('Field is required')
        } else if (this.serverErrors && this.serverErrors.password) {
          return this.serverErrors.password[0]
        } else {
          return null
        }
      },
      touch(field) {
        if (this.serverErrors && this.serverErrors[field]) {
          this.serverErrors[field] = null
        }
        this.$v[field].$touch()
      },
      logout() {
        this.$store.dispatch('auth/logout')
      },
      async submit() {
        if (!this.$v.$invalid) {
          this.loading = true
          try {
            await this.$store.dispatch('auth/login', {
              username: this.email,
              password: this.password
            })
            // await this.$store.dispatch('auth/checkTerms')
            this.$router.push('dashboard')
          } catch (err) {
            this.serverErrors = err.response.data
            this.$v.$touch()
          }
          this.loading = false
        } else {
          this.$v.$touch()
        }
      }
    },
    validations: {
      email: {
        required,
        email,
        serverValidation: serverValidation('email')
      },
      password: {
        required,
        serverValidation: serverValidation('password')
      }
    }
  }
</script>

<style scoped>
  .auth-message {
    font-size: 16px;

  }
</style>
