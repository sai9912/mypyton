<template>
    <b-card no-body class="mt-3 mb-3 collapse-block" :class="{'form-accordion--small': small}">
        <b-card-header header-tag="header" class="p-1 collapse-activator-block" role="tab">
            <div @click="visibleModel = !visibleModel" class="collapse-activator">
                <slot name="header"></slot>
                <i class="material-icons" v-if="visibleModel">expand_less</i>
                <i class="material-icons" v-else>expand_more</i>
            </div>
        </b-card-header>
        <b-collapse
                role="tabpanel"
                v-model="visibleModel"
                :id="id"
        >
            <b-card-body>
                <slot name="body"></slot>
            </b-card-body>
        </b-collapse>
    </b-card>
</template>

<script>
    export default {
        name: "FormAccordion",
        props: {
            visible: {
                required: false,
                default: false
            },
            small: {
                required: false,
                default: false
            }
        },
        data() {
            return {
                id:this._uid.toString(),
                visibleModel: this.visible
            }
        },
        watch: {
            visible(val) {
                this.visibleModel = val;
            },
            visibleModel(val) {
                // to have an ability for other tabs auto collapsing if required (optional)
                this.$emit('on_visibility_change', {'name': this.name, 'val': val});
            },
        }
    }
</script>

<style scoped>
    .collapse-block {
        background-color: #fff;
    }

    .collapse-activator-block {
        background-color: #fff;
    }

    .collapse-activator {
        display: flex;
        color: #002c6c;
        font-size: 1.5rem;
        padding: 5px;
        cursor: pointer;
        align-items: center;
        justify-content: space-between;
    }

    .form-accordion--small .collapse-activator {
        padding: 0px 5px;
        font-size: 1rem;
        color: #676a6c;
    }

</style>
