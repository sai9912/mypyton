<template>
    <form method="post" class="form-horizontal">
        <fieldset>
            <legend>{{ gettext('Packaging Level') }}</legend>
            <p>
                {{ gettext(
                    'Products are packaged at different levels, and each level requires ' +
                    'a specific type of barcode. Choose the option below that best describes ' +
                    'the packaging of your product.') }}
            </p>

            <p class="fieldset">
                {{ gettext(
                    'Note: Packaging levels are heirarchical, which means that you define the lowest ' +
                    'level (base unit/each) first before proceeding to a higher level e.g. a case.') }}
            </p>

            <div class="row" v-if="!loading">
                <div class="col-5">
                    <table style="width:100%; height:100%">
                        <tr>
                            <td align="center" valign="middle">
                                <img id="img-hiearchy" 
                                   :src="image"
                                  style="max-height:180px; max-width:250px;" />
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="col-7 package-list-selector">
                    <h3 style="margin-left: 30px;margin-bottom: 0">{{ gettext('Level') }}</h3>
                    <div class="form-group">
                        <label class="control-label" for="package_level"></label>
                        <ul id="package_level">
                            <li v-for="levelData in packageLevelList">
                                <input type="radio" :value="levelData.id" :id="levelData.id" v-model="packageLevel" />
                                <label class="radio-label" :for="levelData.id" v-text="getTranslated(levelData.label_i18n, languageSlug, fallbackLanguages)"></label>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <spinner-indicator :loading="loading" class="main-spinner"></spinner-indicator>
            <hr/>
            <div class='row'>
                <div class="col-12 text-right">
                    <input class='btn btn-primary' type="submit" @click.prevent="next" v-bind:value="gettext('Next')" :disabled="loading">
                </div>
            </div>
        </fieldset>
    </form>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex';
import TranslationService from '../../common/services/TranslationService';
import _ from 'lodash';
import SpinnerIndicator from "../../common/components/SpinnerIndicator";

export default {
    components:{
        SpinnerIndicator
    },
    data() {
        return {};
    },
    computed: {
        packageLevel: {
            get() {
                return this.$store.state.ProductCreation.packageLevel;
            },
            set(val) {
                this.$store.commit('ProductCreation/setPackageLevel', val);
            }
        },
        image() {
            let packageLevel = _.find(this.packageLevelList, ({id}) => id === this.packageLevel);
            if (packageLevel && packageLevel.image_url) {
                return packageLevel.image_url;
            }
            return '/static/products/site/wizard/packaging-level.gif';
        },
        ...mapState({
            packageLevelList: state => state.ProductCreation.packageLevelList,
            languageSlug: state => state.ProductCreation.language,
            fallbackLanguages: state => state.ProductCreation.fallbackLanguages,
            loading: state => state.ProductCreation.loading,
        }),
    },
    methods: {
        gettext(text) {
            return gettext(text);
        },
        getTranslated(i18n_field) {
            return TranslationService.getTranslated(
                i18n_field, this.languageSlug, this.fallbackLanguages
            );
        },
        ...mapActions({
            next: 'ProductCreation/nextStep'
        })
    }
}
</script>

<style scoped>
    label {
        font-weight: bold;
    }
    .main-spinner
    {
        margin-top: 80px;
        margin-bottom: 80px;
    }
    .radio-label
    {
        margin-left: 5px;
    }
</style>
