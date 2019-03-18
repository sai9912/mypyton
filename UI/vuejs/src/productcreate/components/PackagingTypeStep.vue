<template>
    <form method="post" class="">
        <fieldset>
            <p>{{ gettext(
                'The purpose of this step is to show you where to place the barcode on your products ' +
                'and select the appropriately sized barcode symbol. Barcode symbols are placed ' +
                'where they can be best scanned at point-of-sale as shown below by these general ' +
                'example pictures.') }}</p>
            <h3 class="small-legd mb-2">{{ gettext('PRODUCT AND PACKAGING TYPES') }}</h3>
            <div class="row">
                <div class="col-4">
                    <field-with-errors
                            v-model="packageType" :name="'package_type'" valuetype="string"
                            :choices="packageTypeChoices"
                            :label="'<b>' + gettext('Package type') + '</b>'"
                    ></field-with-errors>
                </div>
                <div class="col-8">
                    <label>
                        <b>{{ gettext('Packaging example') }}:</b>
                    </label>


                    <template v-if="images.length>1">
                        <swiper :options="swiperOption" :key="packageType">
                            <swiper-slide v-for="(image,index) in images" :key="index">
                                <img :src="image"
                                     style="height: 150px;">
                            </swiper-slide>
                            <div class="swiper-button-prev" slot="button-prev"></div>
                            <div class="swiper-button-next" slot="button-next"></div>
                        </swiper>
                    </template>
                    <div v-else>
                        <img :src="images[0]"
                             style="height: 150px;">
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-4">
                </div>
                <div class="col-8">
                    <label>
                        <b>{{ gettext('Packaging definition') }}:</b>
                    </label>
                    <p id="description">{{description}}</p>
                </div>
            </div>
            <hr/>
            <div class="row">
                <div class="col-12 text-right">
                    <a class='btn btn-default' @click.prevent="prev">{{ gettext('Previous') }}</a>
                    <input class='btn btn-primary' type="submit" @click.prevent="next" v-bind:value="gettext('Next')"/>
                </div>
            </div>
        </fieldset>
    </form>
</template>

<script>
    import {mapState, mapActions} from 'vuex';
    import FieldWithErrors from '../../common/components/FieldWithErrors';
    import TranslationService from '../../common/services/TranslationService';
    import _ from 'lodash';
    import '../../assets/swiper.css'
    import {swiper, swiperSlide} from 'vue-awesome-swiper'


    export default {
        data() {
            return {
                imageByType: {},
                descriptionByType: {},
                swiperOption: {
                    grabCursor: true,
                    slidesPerView: 'auto',
                    spaceBetween: 40,
                    navigation: {
                        nextEl: '.swiper-button-next',
                        prevEl: '.swiper-button-prev'
                    }
                }
            };
        },
        computed: {
            packageType: {
                get() {
                    return this.$store.state.ProductCreation.packageType;
                },
                set(val) {
                    this.$store.commit('ProductCreation/setPackageType', val);
                }
            },
            images() {
                if (this.imageByType[this.packageType]) {
                    return this.imageByType[this.packageType];
                }
                return [''];
            },
            description() {
                if (this.descriptionByType[this.packageType]) {
                    return this.descriptionByType[this.packageType];
                }
                return '';
            },
            packageTypeChoices() {
                return _.map(this.packageTypeList, ({id, label_i18n, image_url, description_i18n}) => {
                    this.imageByType[id] = image_url.split(';');
                    this.descriptionByType[id] = this.getTranslated(description_i18n);
                    return [id, this.getTranslated(label_i18n)];
                });
            },
            ...mapState({
                packageTypeList: state => state.ProductCreation.packageTypeList,
                languageSlug: state => state.ProductCreation.language,
                fallbackLanguages: state => state.ProductCreation.fallbackLanguages,
            })
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
                next: 'ProductCreation/nextStep',
                prev: 'ProductCreation/prevStep',
            })
        },
        components: {
            FieldWithErrors,
            swiper,
            swiperSlide
        }
    }
</script>

<style scoped>
    .swiper-slide {
        width: auto;
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .swiper-button-next.swiper-button-disabled, .swiper-button-prev.swiper-button-disabled
    {
        display: none;
    }
</style>

