<template>
    <label class="file-select form-control">
        <div>
            <span class="btn btn-secondary">{{ gettext("Choose file") }}</span>
            <span v-if="value">{{ value.name }}</span>
            <span v-else>{{ gettext("No file chosen") }}</span>
        </div>

        <input type="file"
               @change="handleFileChange"
               ref="image"
               :accept="accept"
        />
    </label>
</template>

<script>
    export default {
        name: "fileSelect",
        props: {
            value: {
                required: true
            },
            accept: {
                required: false
            }
        },
        methods: {
            gettext(val) {
                return gettext(val);
            },
            handleFileChange(e) {
                this.$emit('input', e)
            }
        },
        watch: {
            value(val) {
                if (!val) {
                    this.$refs.image.value = '';
                }
            }
        }
    }
</script>

<style scoped>


    .file-select > input[type="file"] {
        display: none;
    }
</style>
