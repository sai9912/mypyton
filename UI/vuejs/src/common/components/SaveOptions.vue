<template>
    <div class="buttons-block">
        <div v-if="isOptedOutAllowed && packageLevel==70" class="row">
            <div class="col-12">
                <b-form-checkbox v-model="is_opted_out" :disabled="!is_opted_out_enabled" class="opted-out-checkbox">
                    {{ is_opted_out_title }}
                </b-form-checkbox>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div v-if="!isLoading">
                    <b-button variant="info"
                              @click.prevent="button1_save"
                              :disabled="!is_button1_enabled"
                    >
                        {{ button1_title }}
                    </b-button>
                    <b-button variant="primary"
                              @click.prevent="button2_save"
                              :disabled="!is_button2_enabled"
                              v-if="packageLevel==70"
                    >
                        {{ button2_title }}
                    </b-button>
                    <b-button
                            v-if="isStaff && this.gs1_state_value === 'ACTIVE'"
                            variant="warning"
                            @click.prevent="button3_save"
                    >
                        {{ gettext('Save as Draft') }}
                    </b-button>
                </div>
                <div v-if="isLoading" class="loading">
                    <self-building-square-spinner
                            :animation-duration="5000"
                            :size="30"
                            color="#f26334"
                    ></self-building-square-spinner>
                </div>

            </div>
        </div>

        <activate-modal @ok="activate" :text="activateDisclaimerText" ref="activateModal">
        </activate-modal>

        <message-modal :is-open="isDenyActivationModelOpen"
                       :header="gettext('You can not activate this product.')"
                       @close="isDenyActivationModelOpen = false"
        >
            <p>
                {{gettext('These fields should be filled:')}}
            </p>

            <ul>
                <li v-for="error in activationErrors">
                    <strong>{{error.field}}</strong>
                </li>
            </ul>
        </message-modal>
    </div>
</template>

<script>
    import ActivateModal from './ActivateModal';
    import MessageModal from './modals/MessageModal';
    import {SelfBuildingSquareSpinner} from 'epic-spinners'
    import _ from 'lodash';

    const cloudRequiredFields = ['target_market', 'gln_of_information_provider', 'language'];

    export default {
        components: {
            ActivateModal,
            SelfBuildingSquareSpinner,
            MessageModal
        },
        model: {
            prop: 'gs1_state_value',
            event: 'change',
        },
        props: {
            gs1_state_value: {
                required: true,
            },
            isFormDataChanged: {
                required: true,
            },
            isOptedOutAllowed: {
                required: true,
            },
            activateDisclaimerText: {
                required: true,
            },
            isStaff: {
                required: false,
            },
            isEditForm: {
                required: false,
                default: false
            },
            isLoading: {
                required: false,
                default: false
            },
            packageLevel:{
                required: true
            },
            formData: {
                required: true
            }
        },
        data() {
            return {
                is_opted_out: this.gs1_state_value === 'OPTED_OUT',  // initial status,
                isDenyActivationModelOpen: false
            };
        },
        computed: {
            is_opted_out_enabled() {
                return _.includes(['DRAFT', 'OPTED_OUT'], this.gs1_state_value);
            },
            is_button1_enabled() {
                // return this.gs1_state_value !== 'ACTIVE';
                // currently always enabled
                return true;
            },
            is_button2_enabled() {
                let is_activated = this.gs1_state_value === 'ACTIVE';
                return !this.is_opted_out && !is_activated;
            },
            is_opted_out_title() {
                if (this.is_opted_out) {
                    return gettext('Opted out from GS1 Cloud');
                } else {
                    return gettext('Opt out from GS1 Cloud')
                }
            },
            button1_title() {

                if (this.gs1_state_value === 'ACTIVE') {
                    if (this.isFormDataChanged) {
                        return gettext('Update')
                    } else {
                        return gettext('Saved')
                    }
                } else {
                    if (this.isEditForm) {
                        if (this.isFormDataChanged) {
                            return gettext('Update draft')
                        } else {
                            return gettext('Saved as draft')
                        }
                    } else {
                        return gettext('Save as draft')
                    }

                }
            },
            button2_title() {
                if (this.gs1_state_value === 'ACTIVE') {
                    return gettext('Activated')
                } else {
                    return gettext('Activate barcode/GTIN')
                }
            },
            activationErrors() {
                return cloudRequiredFields.filter((key) => {
                    return !this.formData[key].value || this.formData[key].value === '';
                }).map((key) => {
                    return {
                        field: this.formData[key].title
                    }
                });
            },
            isDenyActivation() {
                return this.activationErrors.length > 0;
            }
        },
        methods: {
            gettext(text) {
                return gettext(text);
            },
            button1_save() {
                if (this.gs1_state_value === 'ACTIVE') {
                    // update button doesn't clear ACTIVE status
                    this.$emit('form-submit');
                    return;
                }

                if (this.is_opted_out) {
                    this.$emit('change', 'OPTED_OUT');
                } else {
                    this.$emit('change', 'DRAFT');
                }
                this.$emit('form-submit');
            },
            button2_save() {
                if (this.isDenyActivation) {
                    this.isDenyActivationModelOpen = true;
                    this.setFormError();
                } else {
                    this.$refs.activateModal.open();
                }

            },
            setFormError() {
                const errors = {};
                cloudRequiredFields.filter((key) => {
                    return !this.formData[key].value || this.formData[key].value === '';
                }).forEach((key) => {
                    errors[key] =  [this.gettext("This field is required for activation.")]
                });
                this.$emit('set-errors', errors);
            },
            button3_save() {
                // staff-only button to reset "ACTIVE" to "DRAFT"
                this.$emit('change', 'DRAFT');
                this.$emit('form-submit');
            },
            activate() {
                this.$emit('change', 'ACTIVE');
                this.$emit('form-submit');
            },
        },
        watch: {},
        mounted() {

        }
    }
</script>

<style scoped>
    .opted-out-checkbox {
        padding-bottom: 15px;
    }

    .buttons-block {
        display: inline-block;
        float: right;
    }

    .loading {
        margin-top: 5px;
        margin-right: 75px;
    }
</style>
