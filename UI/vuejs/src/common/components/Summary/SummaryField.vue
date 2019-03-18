<template>
    <div v-if="show" class="row summary">
        <div class="col-4 summary-title">
            <span v-if="title">
                 {{title}}:
            </span>
            <span v-else>
                {{field.title}}:
            </span>

        </div>
        <div class="col-8 summary-value">
            <span v-if="!uom && !field.enum && !value">
                {{field.value}}
            </span>
            <span v-else-if="field.enum">
                {{enumName}}
            </span>
            <span v-else-if="value">
                {{value}}
            </span>
            <span v-else>
               {{field.value}} {{uomName}}
            </span>
        </div>

    </div>
</template>

<script>
    export default {
        name: "SummaryField",

        props: {
            title: {
                type: String,
                required: false
            },
            uom: {
                type: Object,
                required: false,
                default: null
            },
            value: {
                type: String,
                required: false,
            },
            field: {
                type: Object,
                required: true,
                default: null
            },
            alwaysShow: {
                required: false,
                default: false
            }
        },
        data() {
            return {}
        },
        computed: {
            show() {
                return this.field.type !== 'hidden' || this.alwaysShow
            },
            uomName() {
                if (this.uom.value) {
                    const en = this.uom.enum.find((en) =>  en[0] == this.uom.value);
                    return en && en[1]
                }
                return '';
            },
            enumName() {
                if (this.field) {
                    const item = this.field.enum.find(item => item[0] == this.field.value)
                    return item && item[1];
                }
                return ''
            }
        }
    }
</script>

<style scoped>
    .summary {
        margin-bottom: 6px;
    }

    .summary-title {
        font-weight: 600;
    }

    .summary-value {
        font-weight: 300;
    }
</style>
