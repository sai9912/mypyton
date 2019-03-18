<template>
    <b-modal v-model="opened" class="base-agreement-modal">
        <div slot="modal-header" class="container">
            <button type="button" class="close" @click.prevent="opened = false">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{{ gettext('Close') }}</span>
            </button>
            <h4 class="modal-title">{{ title_text }}</h4>
        </div>

        <div class="row">
            <div class="col-12">
                <p class="">
                    {{ text }}
                </p>
                <p class="text-center agreed-checkbox">
                    <b-form-checkbox v-model="agreed" class="opted-out-checkbox">
                        {{ gettext('I agree') }}
                    </b-form-checkbox>
                </p>
            </div>
        </div>

        <div slot="modal-footer" class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <button @click.prevent="opened = false" type="button" class="btn btn-info" data-dismiss="modal">
                        {{ gettext('Cancel') }}
                    </button>
                    <button @click="ok" :disabled="!agreed" data-dismiss="modal" type="button" class="btn btn-primary float-right">
                        {{ gettext('OK') }}
                    </button>
                </div>
            </div>
        </div>
    </b-modal>
</template>

<script>

export default {
    props: {
        title_text: {
            required: false
        },
        text: {
            required: false
        },
        opened: {
            required: true
        },
    },
    data() {
        return {
            opened: false,
            agreed: false,
            text: this.text || '--',
            title_text: this.title_text || '--',
        };
    },
    methods: {
        gettext(text) {
            return gettext(text);
        },
        open() {
            this.opened = true;
        },
        ok() {
            this.opened = false;
            this.$emit('ok', true);
        },
    },
    watch: {},
}
</script>

<style lang="stylus">
    .base-agreement-modal {
        overflow-y: hidden;
        .container {
            margin: 0;
        }
    }
    .agreed-checkbox {
        margin-bottom: 0;
    }
</style>
