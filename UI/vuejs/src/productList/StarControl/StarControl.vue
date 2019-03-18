<template>
  <span class="star-control" @click="change()">
    <i class="fas fa-star selected" v-if="valueModel"></i>
    <i class="far fa-star" v-else></i>
  </span>

</template>

<script>
    import ProductsService from "../../common/services/ProductsService";

    export default {
        name: 'StarControl',
        props: {
            value: {
                required: true
            },
            readonly: {
                required: false,
                default: false
            },
            gtin: {
                required: false
            }
        },
        data() {
            return {
                valueModel: this.value
            }
        },
        methods: {
            change() {
                if (!this.readonly) {
                    this.valueModel = !this.valueModel
                    this.$emit('input', this.valueModel)

                    const product = {
                        mark: this.valueModel ? 1 : 0
                    }
                    ProductsService.patch(this.gtin, product)

                }
            }
        }
    }
</script>

<style scoped>
    .star-control {
        font-size: 16px;
        cursor: pointer;
    }

    .selected {
        color: #ffda76;
    }
</style>
