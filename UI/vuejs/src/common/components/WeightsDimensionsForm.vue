<template>
    <div>

        <form-accordion :visible="visibleWeight" v-if="isWeightsShowed">
            <template slot="header">
                <span>{{ gettext('Weights') }}</span>
            </template>
            <template slot="body">
                <div class='row'>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.gross_weight.errors"
                                v-model="formData.gross_weight.value"
                                :label="formData.gross_weight.title"
                                :name="'gross_weight'"
                                :required="formData.width.required"
                                :valuetype="formData.gross_weight.type"
                                :disabled="!formData.gross_weight_uom.value"
                                :description="formData.gross_weight.description"
                                :readonly="formData.gross_weight.readonly"
                                @click.native="click(formData.gross_weight)"
                        ></field-with-errors>
                    </div>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.gross_weight_uom.errors"
                                :data="formData.gross_weight_uom.value"
                                @change="changeUom('gross_weight_uom', $event)"
                                :label="'&nbsp;'"
                                :name="'gross_weight_uom'"
                                :required="formData.width.required"
                                :valuetype="formData.gross_weight_uom.type"
                                :choices="formData.gross_weight_uom.enum"
                                :description="formData.gross_weight_uom.description"
                                :readonly="formData.gross_weight_uom.readonly"
                                @click.native="click(formData.gross_weight_uom)"
                        ></field-with-errors>
                    </div>
                </div>
                <div class='row' v-if="formData.package_level.value === 70">
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.net_weight.errors"
                                v-model="formData.net_weight.value"
                                :label="formData.net_weight.title"
                                :name="'net_weight'"
                                :required="formData.width.required"
                                :valuetype="formData.net_weight.type"
                                :disabled="!formData.net_weight_uom.value"
                                :description="formData.net_weight.description"
                                :readonly="formData.net_weight.readonly"
                                @click.native="click(formData.net_weight)"
                        ></field-with-errors>
                    </div>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.net_weight_uom.errors"
                                :data="formData.net_weight_uom.value"
                                @change="changeUom('net_weight_uom', $event)"
                                :label="'&nbsp;'"
                                :name="'net_weight_uom'"
                                :required="formData.width.required"
                                :valuetype="formData.net_weight_uom.type"
                                :choices="formData.net_weight_uom.enum"
                                :description="formData.net_weight_uom.description"
                                :readonly="formData.net_weight_uom.readonly"
                                @click.native="click(formData.net_weight_uom)"
                        ></field-with-errors>
                    </div>
                </div>
            </template>
        </form-accordion>
        <form-accordion :visible="visibleDimension" v-if="isDimensionsShowed">
            <template slot="header">
                <span>{{ gettext('Dimensions') }}</span>
            </template>
            <template slot="body">
                <div class="row">
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.depth.errors"
                                v-model="formData.depth.value"
                                :label="formData.depth.title"
                                :name="'depth'"
                                :required="formData.width.required"
                                :valuetype="formData.depth.type"
                                :disabled="!formData.depth_uom.value"
                                :description="formData.depth.description"
                                :readonly="formData.depth.readonly"
                                @click.native="click(formData.depth)"
                        ></field-with-errors>
                    </div>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.depth_uom.errors"
                                :data="formData.depth_uom.value"
                                @change="changeUom('depth_uom', $event)"
                                :label="'&nbsp;'"
                                :name="'depth_uom'"
                                :required="formData.width.required"
                                :valuetype="formData.depth_uom.type"
                                :choices="formData.depth_uom.enum"
                                :description="formData.depth_uom.description"
                                :readonly="formData.depth_uom.readonly"
                                @click.native="click(formData.depth_uom)"
                        ></field-with-errors>
                    </div>
                </div>
                <div class='row'>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.width.errors"
                                v-model="formData.width.value"
                                :label="formData.width.title"
                                :name="'width'"
                                :required="formData.width.required"
                                :valuetype="formData.width.type"
                                :disabled="!formData.width_uom.value"
                                :description="formData.width.description"
                                :readonly="formData.width.readonly"
                                @click.native="click(formData.width)"
                        ></field-with-errors>
                    </div>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.width_uom.errors"
                                :data="formData.width_uom.value"
                                @change="changeUom('width_uom', $event)"
                                :label="'&nbsp;'"
                                :name="'width_uom'"
                                :required="formData.width.required"
                                :valuetype="formData.width_uom.type"
                                :choices="formData.width_uom.enum"
                                :description="formData.width_uom.description"
                                :readonly="formData.width_uom.readonly"
                                @click.native="click(formData.width_uom)"
                        ></field-with-errors>
                    </div>
                </div>
                <div class='row'>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.height.errors"
                                v-model="formData.height.value"
                                :label="formData.height.title"
                                :name="'height'"
                                :required="formData.width.required"
                                :valuetype="formData.height.type"
                                :disabled="!formData.height_uom.value"
                                :description="formData.height.description"
                                :readonly="formData.height.readonly"
                                @click.native="click(formData.height)"
                        ></field-with-errors>
                    </div>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.height_uom.errors"
                                :data="formData.height_uom.value"
                                @change="changeUom('height_uom', $event)"
                                :label="'&nbsp;'"
                                :name="'height_uom'"
                                :required="formData.width.required"
                                :valuetype="formData.height_uom.type"
                                :choices="formData.height_uom.enum"
                                :description="formData.height_uom.description"
                                :readonly="formData.height_uom.readonly"
                                @click.native="click(formData.height_uom)"
                        ></field-with-errors>
                    </div>
                </div>
            </template>
        </form-accordion>

        <form-accordion :visible="visibleNet" v-if="isNetContentShowed">
            <template slot="header">
                <span>{{ gettext('Net content') }}</span>
            </template>
            <template slot="body">
                <div class="row">
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.net_content.errors"
                                v-model="formData.net_content.value"
                                :label="formData.net_content.title"
                                :name="'net_content'"
                                :valuetype="formData.net_content.type"
                                :disabled="!formData.net_content_uom.value"
                                :description="formData.net_content.description"
                                :required="formData.net_content.required"
                                :readonly="formData.net_content.readonly"
                                @click.native="click(formData.net_content)"
                        >
                        </field-with-errors>
                    </div>
                    <div class='col-6'>
                        <field-with-errors
                                :errors="formData.net_content_uom.errors"

                                :data="formData.net_content_uom.value"
                                @change="changeUom('net_content_uom', $event)"
                                :label="'&nbsp;'"
                                :name="'net_content_uom'"
                                :valuetype="formData.net_content_uom.type"
                                :choices="formData.net_content_uom.enum"
                                :description="formData.net_content_uom.description"
                                :required="formData.net_content_uom.required"
                                :readonly="formData.net_content_uom.readonly"
                                @click.native="click(formData.net_content_uom)"
                        >
                        </field-with-errors>
                    </div>
                </div>
            </template>
        </form-accordion>


    </div>
</template>

<script>
    import FieldWithErrors from './FieldWithErrors';
    import FormAccordion from './FormAccordion';

    export default {

        components: {
            FieldWithErrors,
            FormAccordion
        },
        props: {
            formData: {
                required: true
            },
            visible: {
                required: false,
                default: false
            },
            serverErrors: {
                required: false,
                default: null
            }
        },
        data() {
            return {
                visibleWeight: this.visible,
                visibleDimension: this.visible,
                visibleNet: this.visible,
                weightFormField: [
                    'gross_weight',
                    'gross_weight_uom',
                    'net_weight',
                    'net_weight_uom',
                ],
                dimensionFormField: [
                    'depth',
                    'depth_uom',
                    'width',
                    'width_uom',
                    'height',
                    'height_uom'
                ],
                netFormField: [
                    'net_content',
                    'net_content_uom'
                ]
            }
        },
        computed: {
            isWeightsShowed() {
                return this.weightFormField.some((key) => {
                    return this.formData[key].type !== 'hidden'
                })
            },
            isDimensionsShowed() {
                return this.dimensionFormField.some((key) => {
                    return this.formData[key].type !== 'hidden'
                })
            },
            isNetContentShowed() {
                return this.netFormField.some((key) => {
                    return this.formData[key].type !== 'hidden'
                })
            }
        },
        methods: {
            click(form) {
                this.$emit('click-field', form)
            },
            gettext(text) {
                return gettext(text);
            },
            changeUom(uom, $event) {
                this.formData[uom].value = $event;
                if (!$event) {
                    const field = uom.substring(0, uom.length - 4);
                    this.formData[field].value = '';
                }

            }
        },
        watch: {
            serverErrors(val) {
                if (val) {
                    this.visibleWeight = this.visibleWeight || this.weightFormField.some((key) => {
                        return val[key];
                    })
                    this.visibleDimension = this.visibleDimension || this.dimensionFormField.some((key) => {
                        return val[key];
                    })
                    this.visibleNet = this.visibleNet || this.netFormField.some((key) => {
                        return val[key];
                    })
                }
            }
        }
    }
</script>
<style scoped>

</style>
