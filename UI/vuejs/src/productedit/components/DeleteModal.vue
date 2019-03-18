<template>
    <b-modal v-model="opened" ref="modal" class="DeleteModal">
        <div slot="modal-header" class="container-fluid">
            <button type="button" class="close" @click.prevent="opened = false">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{{ gettext('Close') }}</span>
            </button>
            <h4 class="modal-title" id="ProductDeleteTitle">{{ gettext('Product delete confirmation') }}</h4>
        </div>
        <div slot="modal-footer">
            <button @click.prevent="opened = false" type="button" class="btn btn-primary" data-dismiss="modal">
                {{ gettext('Don\'t delete product') }}
            </button>
            <a class="btn btn-warning d-none">
                {{ gettext('Delete and set') }}
            </a>
            <a @click.prevent="deleteProduct" href="" class="btn btn-warning">
                {{ gettext('Delete only') }}
            </a>
        </div>
        <p>
            {{ gettext('You are about to delete one of your products. Because this action will probably create a gap in your serial numbers you must choose what to do.') }}
        </p>
        <ul class="list-unstyled">
            <li>{{ gettext('Delete product and set prefix\'s starting GTIN to deleted product\'s GTIN') }}</li>
            <li><b>{{ gettext('or') }}</b></li>
            <li>{{ gettext('Delete product and don\'t change the starting GTIN of this prefix') }}</li>
        </ul>
        <p>{{ gettext('Keep in mind that only products that are not part of a container can be deleted.') }}</p>
    </b-modal>
</template>

<script>
import { Modal } from 'uiv';
import Token from '../../common/services/TokenService';

export default {
    data() {
        return {
            opened: false
        };
    },
    methods: {
        open() {
            this.opened = true;
        },
        deleteProduct() {
            this.$http.delete(`/api/v1/products/${this.productGtin}/`).then(response => {
                Token.redirect('/products/js-list/');
            });
        },
        gettext(text) {
            return gettext(text);
        },

    },
    props: {
        productGtin: {
            required: true
        },
    },
    components: {
        Modal
    }
}
</script>

<style lang="scss">
    .DeleteModal {
        overflow-y: hidden
    }
</style>
