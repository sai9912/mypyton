<template>
    <b-modal v-model="opened" class="ActivateModal">
        <div slot="modal-header" class="container-fluid">
            <button type="button" class="close" @click.prevent="opened = false">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{{ gettext('Close') }}</span>
            </button>
            <h4 class="modal-title">{{ gettext('Make a pack of trade items using') }}</h4>
            <h4 class="modal-title"><span v-html="gtin_html()"></span> {{ gettext('as a base') }}</h4>
        </div>

        <div class="row">
            <div class="col-12">
                <p>
                    1) {{ gettext('Choose one from the available GTINs') }}:
                </p>
                <table style="width:100%">
                    <tr>
                        <td :class="{ td_disabled : disabled[0] }">
                            <input type="radio" name="sel"
                                   value="0"
                                   v-model="gtin0"
                                   :disabled="disabled[0]==1"> <span v-html="gtin_html(0)"></span>
                        </td>
                        <td :class="{ td_disabled : disabled[1] }">
                            <input type="radio" name="sel"
                                   value="1"
                                   v-model="gtin0"
                                   :disabled="disabled[1]==1"> <span v-html="gtin_html(1)"></span>
                        </td>
                    </tr>
                    <tr>
                        <td :class="{ td_disabled : disabled[2] }">
                            <input type="radio" name="sel"
                                   value="2"
                                   v-model="gtin0"
                                   :disabled="disabled[2]==1"> <span v-html="gtin_html(2)"></span>
                        </td>
                        <td :class="{ td_disabled : disabled[3] }">
                            <input type="radio" name="sel"
                                   value="3"
                                   v-model="gtin0"
                                   :disabled="disabled[3]==1"> <span v-html="gtin_html(3)"></span>
                        </td>
                    </tr>
                    <tr>
                        <td :class="{ td_disabled : disabled[4] }">
                            <input type="radio" name="sel"
                                   value="4"
                                   v-model="gtin0"
                                   :disabled="disabled[4]==1"> <span v-html="gtin_html(4)"></span>
                        </td>
                        <td :class="{ td_disabled : disabled[5] }">
                            <input type="radio" name="sel"
                                   value="5"
                                   v-model="gtin0"
                                   :disabled="disabled[5]==1"> <span v-html="gtin_html(5)"></span>
                        </td>
                    </tr>
                    <tr>
                        <td :class="{ td_disabled : disabled[6] }">
                            <input type="radio" name="sel"
                                   value="6"
                                   v-model="gtin0"
                                   :disabled="disabled[6]==1"> <span v-html="gtin_html(6)"></span>
                        </td>
                        <td :class="{ td_disabled : disabled[7] }">
                            <input type="radio" name="sel"
                                   value="7"
                                   v-model="gtin0"
                                   :disabled="disabled[7]==1"> <span v-html="gtin_html(7)"></span>
                        </td>
                    </tr>
                    <tr>
                        <td :class="{ td_disabled : disabled[8] }">
                            <input type="radio" name="sel"
                                   value="8"
                                   v-model="gtin0"
                                   :disabled="disabled[8]==1"> <span v-html="gtin_html(8)"></span>
                        </td>
                        <td :class="{ td_disabled : disabled[9] }">
                            <input type="radio" name="sel"
                                   value="9"
                                   v-model="gtin0"
                                   :disabled="disabled[9]==1"> <span v-html="gtin_html(9)"></span>
                        </td>
                    </tr>
                </table>
                <hr/>
                <p>
                    2) {{ gettext('Indicate hierarchy level') }}:
                </p>
                <select v-model="package_level"
                        style="margin-left:20px; padding:0px 10px;">
                    <option v-for="template in templates" v-bind:value="template.id">{{ template.ui_label }}</option>
                </select>
            </div>
        </div>

        <div slot="modal-footer" class="container-fluid">
            <div class="row">
                <div class="col-12 float-right">
                    <b-button variant="primary"
                              @click.prevent="button_ok"
                              class="float-right"
                              style="margin-left:5px">
                        {{ gettext('OK') }}
                    </b-button>
                    <b-button variant="danger"
                              @click.prevent="opened = false"
                              class="float-right">
                        {{ gettext('Cancel') }}
                    </b-button>
                </div>
            </div>
        </div>
    </b-modal>
</template>

<script>

export default {
    data() {
        return {
            templates:[],
            opened: false,
            prefix_length: 9,
            disabled: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            gtin0: -1,
            package_level: 50
        }
    },
    computed: {
    },
    methods: {
        gettext(text) {
            return gettext(text);
        },
        open() {
            this.opened = true;
        },
        button_ok() {
            this.opened = false;
            this.$emit('ok', true);
            console.log('Ok', this.gtin0, this.package_level)
            if (parseInt(this.gtin0) < 0 || parseInt(this.gtin0) > 9) {
                return
            }
            let productFormData = new FormData();
            let subproduct_gtin = this.gtin
            let newproduct_gtin = '' + this.gtin0 + this.gtin.substring(1)
            let newproduct_gtin_chk = this.calculate_chk(newproduct_gtin)
            newproduct_gtin = newproduct_gtin.substring(0, newproduct_gtin.length-1) + newproduct_gtin_chk
            productFormData.set('subproduct_gtin', subproduct_gtin)
            productFormData.set('newproduct_gtin', newproduct_gtin)
            productFormData.set('package_level', this.package_level)

            if (subproduct_gtin.match(/\d+/) &&
                newproduct_gtin.match(/\d+/) &&
                this.package_level.toString().match(/\d+/)) {
                let request_url = '/api/v1/products/clone/';
                this.$http.post(request_url, productFormData).then(
                    response => {
                        console.log(response)
                        let new_url = '/products/' + response.body.product_id + '/fulledit_js/'
                        document.location.href = new_url
                    },
                    (response) => {
                        this.$emit('errors', response.body)
                    }
                );
            }
        },
        getapi_available_gtins() {
            let request_url = '/api/v1/products/clone/';
            let productFormData = new FormData();
            productFormData.set('gtin', this.gtin)
            this.$http.put(request_url, productFormData).then(
                response => {
                    console.log(response)
                    this.disabled = response.body.existed
                    this.templates = response.body.templates
                    this.gtin0 = -1
                    for(let i in this.disabled) {
                        if (this.disabled[i] == 0) {
                            this.gtin0 = i
                            break
                        }
                    }
                    if (this.templates.length > 0) {
                        this.package_level = this.templates[0].id
                    }
                },
                (response) => {
                    this.$emit('errors', response.body)
                }
            );
        },
        calculate_chk(gtin) {
            let result = 0;
            let core = gtin.substring(0, gtin.length-1)
            for (let counter = core.length - 1; counter >= 0; counter--) {
                if (counter % 2) {
                    result = result + parseInt(core.charAt(counter))
                } else {
                    result = result + parseInt(core.charAt(counter)) * 3
                }
            }
            let chk = (10 - (result % 10)) % 10;
            return chk
        },
        gtin_html: function(gtin0) {
            if (gtin0 === undefined) {
                gtin0 = this.gtin[0]
            }
            let gtin_main = this.gtin.substring(1, this.prefix_length+1)
            let gtin_counter = this.gtin.substring(this.prefix_length+1, this.gtin.length-1)
            let gtin_chk = this.calculate_chk(gtin0 + this.gtin.substring(1))
            return gtin0 + ' <b>' + gtin_main + '</b> <span style="color:red">' + gtin_counter + '</span> ' + gtin_chk
        }
    },
    props: {
        gtin: {
            required: false
        },
    },
    components: {
    },
    mounted() {
        this.getapi_available_gtins()
    }
}
</script>

<style lang="scss">
    .ActivateModal {
        overflow-y: hidden;
        tr:nth-child(odd) {
            background-color: #EEE
        }
        td {
            padding-left: 20px
        }
        .td_disabled {
            opacity: 0.5
        }
    }

</style>
