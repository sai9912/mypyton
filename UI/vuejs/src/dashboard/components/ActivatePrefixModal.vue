<template>
    <b-modal v-model="opened" class="activate-prefix-modal">
        <div slot="modal-header" class="container-fluid">
            <button type="button" class="close" @click.prevent="opened = false">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{{ gettext('Close') }}</span>
            </button>
            <h4 class="modal-title" id="ProductDeleteTitle">{{ gettext('Prefix activation confirmation') }}</h4>
        </div>

        <div class="row">
            <div class="col-12">
                <p class="">
                    {{ gettext('You have chosen a default prefix.') }}
                    {{ gettext('Next time you click on "Add a new product" this prefix will be used for GTIN allocation.') }}
                </p>
            </div>
        </div>

        <div slot="modal-footer" class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <button @click.prevent="opened = false" type="button" class="btn btn-info" data-dismiss="modal">
                        {{ gettext('Cancel') }}
                    </button>
                    <button @click="ok" data-dismiss="modal" type="button" class="btn btn-primary float-right">
                        {{ gettext('Confirm choice of prefix') }}
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
            opened: false,
            prefix: {},
        };
    },
    methods: {
        gettext(text) {
            return gettext(text);
        },
        open(prefix) {
            this.prefix = prefix;
            this.opened = true;
        },
        ok() {
            this.opened = false;
            this.$emit('ok', this.prefix);
        },
    },
    props: {
    },
    components: {},
}
</script>

<style lang="scss">
    .activate-prefix-modal {
        overflow-y: hidden
    }
</style>
