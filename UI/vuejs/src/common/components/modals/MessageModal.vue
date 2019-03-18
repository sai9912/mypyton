<template>
    <b-modal v-model="openModel" class="message-modal" @hide="close()">
        <div slot="modal-header" class="container-fluid">
            <button type="button" class="close" @click.prevent="close()">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{{ gettext('Close') }}</span>
            </button>
            <h4 class="modal-title" id="ProductDeleteTitle">{{header}}</h4>
        </div>

        <div class="row">
            <div class="col-12">
                <slot></slot>
            </div>
        </div>

        <div slot="modal-footer" class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <button @click="close()" data-dismiss="modal" type="button"
                            class="btn btn-primary float-right">
                        {{ gettext('OK') }}
                    </button>
                </div>
            </div>
        </div>
    </b-modal>
</template>

<script>

    export default {
        data() {
            return {
                openModel: this.isOpen,
            };
        },
        methods: {
            gettext(text) {
                return gettext(text);
            },
            close() {
                this.openModel = false;
                this.$emit('close');
            }
        },
        props: {
            header: {
                required: true
            },
            isOpen: {
                required: true
            }
        },
        watch: {
            isOpen(val) {
                this.openModel = val;
            }
        },
        components: {},
    }
</script>

<style lang="scss">
    .message-modal {
        overflow-y: hidden
    }
</style>
