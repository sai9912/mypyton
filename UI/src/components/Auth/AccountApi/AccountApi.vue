<template>
  <div class="loginForm">

    <form @submit.prevent="submit" name="loginForm" novalidate="true">

      <b-form-group
        :label="$t('AccountApi.CompanyGLN')"
        horizontal
        :label-cols="4"
        label-for="uuid"
        :invalid-feedback="invalidFeedback('uuid')"
        :state="$v.uuid.$error?false:null"
      >
        <b-form-input
          id="uuid"
          name="uuid"
          :state="$v.uuid.$error?false:null"
          @change="touch('uuid')"
          v-model.trim="uuid">
        </b-form-input>
      </b-form-group>

      <b-form-group
        :label="$t('Email')"
        horizontal
        :label-cols="4"
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
        :label="$t('Prefix')"
        horizontal
        :label-cols="4"
        label-for="company_prefix"
        :invalid-feedback="invalidFeedback('company_prefix')"
        :state="$v.company_prefix.$error?false:null"
      >
        <b-form-input
          id="company_prefix"
          name="company_prefix"
          :state="$v.company_prefix.$error?false:null"
          @change="touch('company_prefix')"
          v-model.trim="company_prefix">
        </b-form-input>
      </b-form-group>

      <b-form-group
        :label="$t('AccountApi.CompanyName')"
        horizontal
        :label-cols="4"
        label-for="company_name"
        :invalid-feedback="invalidFeedback('company_name')"
        :state="$v.company_name.$error?false:null"
      >
        <b-form-input
          id="company_name"
          name="company_name"
          v-model.trim="company_name"
          :state="$v.company_name.$error?false:null"
          @change="touch('company_name')"
        >
        </b-form-input>
      </b-form-group>
      <b-form-group
        :label="$t('AccountApi.Credits')"
        horizontal
        :label-cols="4"
        label-for="credits"
        :invalid-feedback="invalidFeedback('credits')"
        :state="$v.credits.$error?false:null"
      >
        <b-form-input
          id="credits"
          name="credits"
          v-model.trim="credits"
          :state="$v.credits.$error?false:null"
          @change="touch('credits')"
        >
        </b-form-input>
      </b-form-group>

      <b-form-group
        :label="$t('AccountApi.TXNRef')"
        horizontal
        :label-cols="4"
        label-for="txn_ref"
        :invalid-feedback="invalidFeedback('txn_ref')"
        :state="$v.txn_ref.$error?false:null"
      >
        <b-form-input
          id="txn_ref"
          name="txn_ref"
          v-model.trim="txn_ref"
          :state="$v.txn_ref.$error?false:null"
          @change="touch('txn_ref')"
        >
        </b-form-input>
      </b-form-group>

      <b-form-group
        :label="$t('AccountApi.GS1MO')"
        horizontal
        :label-cols="4"
        label-for="member_organisation"
      >
        <b-form-select name="member_organisation" v-model="member_organisation" :options="memberOrganizations"/>
      </b-form-group>

      <div v-if="serverErrors && serverErrors.non_field_errors">
        <p class="text-danger" v-for="item in serverErrors.non_field_errors">{{item}}</p>
      </div>


      <vue-ladda button-type="submit" :loading="loading" :error="serverErrors" data-style="expand-right">Submit</vue-ladda>
    </form>


  </div>
</template>

<script>
  import {required, email} from 'vuelidate/lib/validators'
  import {serverValidation} from '../../../helpers/vuelidate'

  const memberOrganizations = [
    {value: 'gs1au', text: 'GS1 Australia'},

    {value: 'gs1belu', text: 'GS1 Belgium'},

    {value: 'gs1bih', text: 'GS1 Bosnia Herzegovina'},

    {value: 'gs1cz', text: 'GS1 Czech'},

    {value: 'gs1eg', text: 'GS1 Egypt'},

    {value: 'gs1fi', text: 'GS1 Finland'},

    {value: 'gs1fr', text: 'GS1 France'},

    {value: 'gs1de', text: 'GS1 Germany'},

    {value: 'gs1go', text: 'GS1 GO'},

    {value: 'gs1gr', text: 'GS1 Greece'},

    {value: 'gs1hk', text: 'GS1 Hong Kong'},

    {value: 'gs1ie', text: 'GS1 Ireland'},

    {value: 'gs1it', text: 'GS1 Italy'},

    {value: 'gs1my', text: 'GS1 Malaysia'},

    {value: 'gs1za', text: 'GS1 South Africa'},

    {value: 'gs1se', text: 'GS1 Sweden'},

    {value: 'gs1ch', text: 'GS1 Switzerland'},

    {value: 'gs1uk', text: 'GS1 UK'}
  ]

  export default {
    name: 'Login',
    data() {
      return {
        uuid: '',
        email: '',
        company_prefix: '',
        company_name: null,
        credits: null,
        txn_ref: null,
        member_organisation: memberOrganizations[0].value,
        memberOrganizations: memberOrganizations,
        serverErrors: null,
        loading: false
      }
    },
    computed: {},
    methods: {
      submit() {
        if (!this.$v.$invalid) {
          this.loading = true
          this.$store.dispatch('accountApi/register', {
            uuid: this.uuid,
            email: this.email,
            company_prefix: this.company_prefix,
            company_name: this.company_name,
            credits: this.credits,
            txn_ref: this.txn_ref,
            member_organisation: this.member_organisation
          }).then(() => {
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
      },
      invalidFeedback(field) {
        if (this.$v[field].required !== undefined && !this.$v[field].required) {
          return this.$t('Field is required')
        } else if (this.serverErrors && this.serverErrors[field]) {
          return this.serverErrors[field][0]
        } else {
          return null
        }
      },
      invalidFeedbackEmail() {
        if (!this.$v.email.required) {
          return this.$t('Field is required')
        } else if (this.serverErrors && this.serverErrors['email']) {
          return this.serverErrors['email'][0]
        } else if (!this.$v.email.email) {
          return this.$t('Email is incorrect')
        } else {
          return null
        }
      },
      touch(field) {
        if (this.serverErrors && this.serverErrors[field]) {
          this.serverErrors[field] = null
        }
        this.$v[field].$touch()
      }
    },
    validations: {
      uuid: {
        required,
        serverValidation: serverValidation('email')
      },
      email: {
        required,
        email,
        serverValidation: serverValidation('email')
      },
      company_prefix: {
        required,
        serverValidation: serverValidation('company_prefix')
      },
      company_name: {
        serverValidation: serverValidation('company_name')
      },
      credits: {
        serverValidation: serverValidation('credits')
      },
      txn_ref: {
        serverValidation: serverValidation('txn_ref')
      }
    }
  }
</script>

<style scoped>

  .loginForm {
    max-width: 600px;
  }
</style>
