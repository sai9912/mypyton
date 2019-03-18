<template>
    <div v-if="valuetype !== 'hidden'" class="fields-with-error" :class="{
            'has-error': errors && valuetype  === 'boolean',
            'input-group-checkbox': typeof data === 'boolean',
            'form-group': valuetype  !== 'boolean',
            'input-group': valuetype  === 'boolean',
            'required': required
        }">
        <template v-if="valuetype === 'boolean'">
            <div class="input-group input-group-checkbox" :class="{'required': required}">
                <div class="checkbox">
                    <label>
                        <input type="checkbox" :name="name" :id="name" :checked="model" @change="emitUpdate"
                               :disabled="disabled || readonly" :readonly="readonly"/>
                        {{ label }}
                    </label>
                </div>

                <span v-if="description" class="checkbox-description" v-b-popover.hover="description">
                    <i class="material-icons">info_outline</i>
                </span>
            </div>
        </template>
        <template v-else>
            <label class="control-label" :for="name" v-if="label && label === '&nbsp;'" v-html="label"></label>
            <label class="control-label" :for="name" v-else-if="label" v-html="label"></label>
            <template v-else></template>
            <div class="input-group">


                <input v-if="!choices && valuetype!=='number'"
                       type="text"
                       :name="name"
                       class="form-control"
                       :id="name"
                       v-model="model"
                       :disabled="disabled"
                       :readonly="readonly"/>

                <input v-if="!choices&& valuetype === 'number'" type="number"
                       min="0" :name="name" class="form-control" :id="name" :value="value"
                       @change="emitUpdate" :disabled="disabled" @input="emitUpdate" :readonly="readonly"/>

                <select
                        v-if="choices"
                        :name="name"
                        :id="name"
                        class="form-control"
                        @change="emitUpdate"
                        :disabled="disabled"
                        :readonly="readonly">
                    <option v-for="(val) in choices" v-bind:value="val[0]" :selected="val[0] === value"
                            :disabled="readonly">
                        {{ val[1] }}
                    </option>
                </select>
                <div class="input-group-append" v-b-popover.hover="description" v-if="description">
                    <span class="input-group-text"> <i class="material-icons">info_outline</i></span>
                </div>


                <div class="input-group-append" v-if="language" :id="uid+'_translate'">
                    <span class="input-group-text"> <i class="material-icons">title</i></span>
                </div>

                <b-popover :target="uid+'_translate'" triggers="hover focus" v-if="language">
                    <template slot="title">Localized Field</template>
                    <div v-for="item in languages">
                        <span :class="{'font-weight-bold':item.code === language}">{{item.name}}: {{translateValue[item.code]}}</span>
                    </div>
                </b-popover>


            </div>

            <span class="help-block" v-if="errors">
                <small v-for="error in errors" class="text-danger">{{ error }}</small>
            </span>
        </template>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                value: this.data,
                uid: this._uid
            };
        },
        model: {
            prop: 'data',
            event: 'change'
        },
        computed: {
            model: {
                get: function () {
                    if (this.language) {
                        return this.value && this.value[this.language];
                    }
                    else {
                        return this.value;
                    }
                },
                set: function (value) {
                    if (this.language) {
                        const dict = Object.assign({}, this.value);
                        dict[this.language] = value;
                        this.$emit('change', dict);
                    }
                    else {
                        this.emitUpdate(value)
                    }
                }
            },
            translateValue() {
                return this.value || {}
            }
        },
        methods: {
            emitUpdate(event) {
                let el = event.target;
                if (this.valuetype === 'string') {
                    let val;
                    if (this.choices) {
                        val = el.options[el.selectedIndex].value;
                    } else {
                        val = event;
                    }
                    this.$emit('change', String(val));
                } else if (this.valuetype === 'boolean') {
                    this.$emit('change', el.checked);
                } else if (this.valuetype === 'number') {
                    if (this.value < 0) {
                        this.value = 0;
                        return;
                    }
                    const val = this.choices ? el.options[el.selectedIndex].value : el.value;
                    this.$emit('change', val);
                }
            },
            emitChange(event) {
                this.$emit('changed', event.target.value);
            },
            move()
            {

            }
        },
        watch: {
            disabled(val, oldVal) {
                if (!val && oldVal) {
                    this.data = '';
                }
            },
            data(val) {
                this.value = val;
            }
        },
        props: {
            errors: {
                required: false
            },
            data: {
                required: false
            },
            required: {
                required: false,
                default: false
            },
            label: {
                required: true
            },
            name: {
                required: true
            },
            description: {
                required: false,
                default: undefined
            },
            choices: {
                required: false,
                default: undefined
            },
            valuetype: {
                required: false,
                default: 'string'
            },
            disabled: {
                required: false,
                default: false
            },
            readonly: {
                required: false,
                default: false
            },
            languages: {
                required: false,
            },
            language: {
                required: false,
            }
        },
        mounted: function () {
            if (this.disabled) {
                this.value = '';
            }
        }
    }
</script>
<style>
    .checkbox-description {
        margin-left: auto;
    }

    .control-label {
        font-weight: 600;
    }
</style>