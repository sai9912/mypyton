<template>
    <div>
        <b-form-select class="lang-select" v-model="selected" :options="languages" @input="setLanguage"></b-form-select>
    </div>

</template>

<script>
    import UILanguageService from "../../../../services/UILanguageService";

    export default {
        name: 'Localization',
        props: {
            language: {
                required: true
            }
        },
        data() {
            return {
                languages: [],
                selected: this.language
            }
        },
        computed: {},
        methods: {
            setLanguage(language) {
                UILanguageService.selectLanguage({
                    new_language: language
                }).then(() => {
                    window.location.reload(false);
                })
            }
        },
        mounted() {
            UILanguageService.getList()
                .then(result => {
                    this.languages = result.map((language) => {
                        return {value: language.slug, text: language.name}
                    });
                });
        }
    }
</script>

<style scoped>
    .lang-select {
        width: 130px;
        margin-top: 6px;
        font-size: 14px;
    }
</style>
