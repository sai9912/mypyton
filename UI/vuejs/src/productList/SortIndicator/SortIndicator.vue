<template>
    <th class="sort-indicator"
          @click="changeSort"
          :class="{
           'current':order.key===orderKey
           }"
    >
        <span>
             <slot></slot>
        </span>
        <i class="fas fa-sort" v-if="order.key!==orderKey"></i>
        <i class="fas fa-sort-up" v-if="order.key===orderKey && order.isDesc"></i>
       <i class="fas fa-sort-down" v-if="order.key===orderKey && !order.isDesc"></i>


    </th>
</template>

<script>
    export default {
        name: "SortIndicator",
        props: {
            order: {
                required: true,
                type: Object
            },
            orderKey: {
                required: true,
                type: String
            }
        },
        methods: {
            changeSort() {
                if (this.order.key !== this.orderKey) {
                    this.$emit('change', {
                            key: this.orderKey,
                            isDesc: this.order.isDesc
                        }
                    )
                } else {
                    this.$emit('change', {
                            key: this.orderKey,
                            isDesc: !this.order.isDesc
                        }
                    )
                }
            }
        }
    }
</script>

<style scoped lang="scss">
    .sort-indicator {
        cursor: pointer;
        &:hover{
            background: #f0f0f0;
        }
    }

    .current
    {
        background: #f0f0f0;
    }
</style>