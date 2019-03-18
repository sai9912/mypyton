<template>

    <div
            class="gpc-select"
            :class="{
            'required': required
        }">
        <label class="control-label" for="category"> {{ gettext('Global Product Classification') }}</label>
        <div class="input-group ">
            <v-select label="name"
                      :filterable="false"
                      :options="options"
                      :value="selected"
                      :loading="loading"
                      @input="onSelect($event)"
                      @search="onSearch"
                      :disabled="readonly"
            >
                <template slot="no-options">
                    <span v-if="!searchStr">
                        {{ gettext('Please enter at least 3 characters') }}
                    </span>
                    <span v-if="searchStr">
                        {{ gettext('Results not found') }}
                    </span>
                </template>
                <template slot="option" slot-scope="option">
                    {{option.Brick}} (<strong>{{option.BrickCode}}</strong>)
                </template>
                <template slot="selected-option" slot-scope="option">
                    <span v-if="option.Brick">{{option.Brick}} (<strong>{{option.BrickCode}}</strong>)</span>
                    <span v-else>{{option.BrickCode}}</span>
                </template>
            </v-select>
            <input type="hidden" v-model="value" name="category" id="category"/>

            <div class="input-group-append" v-b-popover.hover="description" v-if="description">
                <span class="input-group-text"> <i class="material-icons">info_outline</i></span>
            </div>
        </div>

        <span class="help-block" v-if="errors">
            <small v-for="error in errors" class="text-danger">{{ error }}</small>
        </span>
    </div>

</template>

<script>
    import vSelect from 'vue-select'
    import _ from 'lodash'
    import GPCServices from './../services/GPCServices'

    export default {
        name: 'GpcSelect',
        components: {
            vSelect
        },
        props: {
            required: {
                required: false,
                default: false
            },
            errors: {
                type: Array
            },
            value: {

            },
            readonly: {
                type: Boolean,
                required: false
            },
            description: {
                type: String,
                required: false
            },
            gpcLoading: {
                type: Boolean,
                required: false,
                default: false
            }
        },
        data() {
            return {
                selected: null,
                options: [],
                searchStr: null,
                loading: false
            }
        },
        methods: {
            onSelect($event) {
                this.selected = $event || '';
                this.$emit('input', this.selected);
                this.$emit('select', this.selected && this.selected.BrickCode || '');
            },
            onSearch(search, loading) {
                if (search.length > 2) {
                    loading(true);
                    this.searchStr = search;
                    this.search(loading, search, this)
                } else {
                    this.searchStr = null;
                    this.options = []
                }
            },
            search: _.debounce((loading, search, vm) => {
                const param = {};
                const isNum = /^\d+$/.test(search);
                if (isNum) {
                    param.brick_code = search
                } else {
                    param.brick = search
                }
                GPCServices.getList(param).then(res => {
                    vm.options = res
                }).finally(() => {
                    loading(false)
                })
            }, 300),
            gettext(text) {
                return gettext(text);
            }
        },
        watch: {
            value(value) {
                this.selected = value
            },
            gpcLoading(value) {
                this.loading = value;
            }
        },
        mounted() {
            if (this.value) {
                this.selected = this.value
            }
            this.loading = this.gpcLoading;
        }
    }
</script>

<style>
    .gpc-select .v-select {
        flex: 1 1 0%
    }

    .gpc-select .v-select .dropdown-toggle {
        display: flex !important;
        flex-wrap: wrap;
        -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
        box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
        border: 1px solid #ced4da;
    }

    .gpc-select .v-select input[type=search], .gpc-select .v-select input[type=search]:focus {
        flex-basis: 20px;
        flex-grow: 1;
        height: 38px;
        padding: 0 20px 0 10px;
        width: 100% !important;
        font-size: 1rem;
    }

    .gpc-select .v-select li > a {
        padding: 5px 20px;
    }

    .gpc-select-block .gpc-select {
        margin-bottom: 0.2rem;
    }

    .gpc-select.required .control-label:after {
        content: " *";
        color: #f00;
    }

    .v-select .selected-tag
    {
        font-size: 1rem;
        margin: 6px 1px 0 3px;
    }
</style>
