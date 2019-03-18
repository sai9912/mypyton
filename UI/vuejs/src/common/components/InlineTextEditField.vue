<template>
    <div id="text-editor">
        <span :class="{'display-none': editor_enabled, 'label': !editor_enabled}" @click="showEditor">
            {{ text || default_text }}
        </span>
        <b-input-group :class="{'display-none': !editor_enabled}">
            <b-form-input
                size="sm"
                v-model="updated_text"
                ref="text_input"
                @keydown.native.enter="saveChanges"
                @keydown.native.esc="cancelChanges"/>

            <b-input-group-append>
                <b-btn size="sm" variant="default" @click="saveChanges">Ok</b-btn>
            </b-input-group-append>
        </b-input-group>
    </div>
</template>

<script>

export default {
    data() {
        return {
            editor_enabled: false,
            updated_text: this.text,
        };
    },
    model: {
        prop: 'text',
        event: 'change'
    },
    methods: {
        gettext(text) {
            return gettext(text);
        },
        showEditor(event) {
            this.editor_enabled = true;
            this.$nextTick(() => this.$refs.text_input.focus());
        },
        cancelChanges(event) {
            this.editor_enabled = false;
            this.updated_text = this.text;
        },
        saveChanges(event) {
            this.editor_enabled = false;
            this.$emit('change', this.updated_text);

            // not necessary cause it possible to pass data directly as argument
            if(this.updated_text !== this.text) {
                this.$emit('ok', this.updated_text);
            }
        },
    },
    props: {
        'text': {
            required: true,
        },
        'default_text': {
            required: false,
            default: '--',
        }
    },
    components: {},
}
</script>

<style lang="scss">
    #text-editor {
        .activate-prefix-modal {
            overflow-y: hidden
        }
        .display-none {
            display: none;
        }
        .label {
            display: inline-block;
            border-bottom: 1px dashed grey;
        }
    }
</style>
