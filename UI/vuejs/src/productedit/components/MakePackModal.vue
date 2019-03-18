<template>
    <b-modal v-model="opened" ref="modal" class="DeleteModal">
        <div slot="header">
            <button type="button" class="close" data-dismiss="modal">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{{ gettext('Close') }}</span>
            </button>
            <h4
                class="modal-title"
                style="padding: 2px 42px; text-align: center; font-size: 1.8em; font-weight: 300;"
            >
                <div>{{ gettext('Make a pack of trade items using') }}</div>
                <div>{{ gtin0 }} {{ gettext('as a base') }}</div>
            </h4>
        </div>
        <div slot="footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">
                {{ gettext('Cancel') }} </button>
            <a href="javascript:void(0);" onclick="return submitMakePack();" class="btn btn-primary">
                {{ gettext('Create') }}
            </a>
        </div>
        <form
            method="get" action="'/products/add/case/details'" enctype="multipart/form-data" id="make_pack_form"
        >
            <input type="hidden" id="hidden_product_id" :value="productId" />
            <div class='row'>
                <div class="pull-left col-xs-9">
                    1) {{ gettext('Choose one from the available GTINs') }}:
                </div>
            </div>
            <table class="table table-striped table-condensed table-borderless" id="gtin-radios">

            </table>

            <hr/>
            <div class='row'>
                <div class="pull-left col-xs-6">
                    2) {{ gettext('Indicate hierarchy level') }}:
                </div>
                <div class="pull-right col-xs-6">
                    <select class="form-control" id="pack_selection">
                        <option value="60" selected>
                            {{ gettext('Pack or inner pack e.g. six pack of beer bottles') }}
                        </option>
                        <option value="50"> {{ gettext('Outer Case e.g. case of beer (bottles or packs)') }}</option>
                        <option value="30"> {{ gettext('Pallet e.g. pallet of cases of beer') }}</option>
                    </select>
                </div>
            </div>
        </form>
    </b-modal>
</template>

<script>
import { Modal } from 'uiv';

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
        gettext(text) {
            return gettext(text);
        },
    },
    props: {
        productId: {
            required: true,
            type: Number
        },
    },
    components: {
        Modal
    }
}
</script>

<style lang="scss">
</style>

