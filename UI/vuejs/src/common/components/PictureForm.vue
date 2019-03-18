<template>
    <form-accordion :visible="visibleModel" v-if="formData.image_i18n.type!=='hidden'">
        <template slot="header">
            <span>{{ gettext('Product Image') }}
            <span style="font-size: 0.6em;vertical-align: middle;">
                ({{ gettext('Upload a picture of your product') }})&nbsp;
            </span></span>
        </template>
        <template slot="body">
            <div class="well">
                <p>
                    {{ gettext(
                    'Please upload an image of your product and/or a publicly-accessible Web URL ' +
                    'of an image of the product. This URL should be for an image (jpg or png), ' +
                    'not for a web page (html). This is a text field and the format will be, for example') }}:
                </p>
                <p>
                    https://www.gs1.org/docs/gs1-cloud/0950400059231.JPG</p>
                <p>
                    {{ gettext(
                    'Including a URL to an image of your product will ensure potential customers ' +
                    'can access the image you want them to see and not something they just find ' +
                    'on the internet. It can also help online market places to have an accurate ' +
                    'representation of your product and help you increase sales.') }}
                </p>
            </div>

            <template v-if="!formData.image_i18n.readonly">
                <div class="well well-sm">
                    {{ gettext('Accepted file types are: JPG, PNG, GIF with a size less than 2 MB') }}
                </div>


            </template>

<<<<<<< HEAD
=======
            <div class="well well-sm">
                <field-with-errors
                        :errors="formData.image_i18n.errors"
                        v-model="formData.image_i18n.value"
                        :label="formData.image_i18n.title"
                        :name="'image_i18n'"
                        :required="formData.image_i18n.required"
                        :valuetype="formData.image_i18n.type"
                        :description="formData.image_i18n.description"
                        :readonly="formData.image_i18n.readonly"
                        @click.native="click(formData.image_i18n)"
                        :languages ="languages"
                        :language = "language"
                >
                </field-with-errors>
            </div>
>>>>>>> issue-495

            <label class="control-label mt-3" for="image">{{formData.image_i18n.title}} <span class="text-danger"
                                                                                                     v-if="formData.image_i18n.required"> *</span>
            </label>


            <b-tabs :value="activeTab" @input="changeTab($event)">

                <b-tab :title="gettext('Upload Image File')">
                    <div class="mt-3">

                        <div class="input-group">


                            <file-select
                                    id="image"
                                    :value="file"
                                    accept="image/*"
                                    @input="imageProcess">
                            </file-select>

                            <div class="input-group-append" v-b-popover.hover="formData.image_i18n.description"
                                 v-if="formData.image_i18n.description">
                                <span class="input-group-text"> <i class="material-icons">info_outline</i></span>
                            </div>

                        </div>

                        <div>
                            <span class="help-block" v-if="formData.image_i18n.errors">
                                <small v-for="error in formData.image_i18n.errors"
                                       class="text-danger">{{ error }}</small>
                            </span>
                        </div>
                    </div>
                </b-tab>
                <b-tab :title="gettext('Paste External Image Url')">
                    <div class="mt-3">
                        <field-with-errors
                                :errors="formData.image_i18n.errors"
                                :data="formData.image_i18n.value"
                                @changed="changeUrl($event)"
                                label=""
                                :name="'image_i18n'"
                                :required="formData.image_i18n.required"
                                :valuetype="formData.image_i18n.type"
                                :description="formData.image_i18n.description"
                                :readonly="formData.image_i18n.readonly"
                                @click.native="click(formData.image_i18n)"
                        >
                        </field-with-errors>
                    </div>
                </b-tab>


            </b-tabs>


            <label class="control-label mt-3">{{gettext('Preview')}}</label>


            <div class="row align-items-center">
                <div class="col">
                    <div class="thumbnail mt-0">

                        <div v-if="!loadError">

                            <div v-show="!isImageChecking">
                                <img v-if="formData.image_i18n.value || isImageChecking" :src="imageUrl"
                                     @load="loadImageSuccess()"
                                     @error="loadImageError()">
                                <img v-else :src="imageData" alt="No image">
                            </div>
                            <spinner-indicator class="mt-3" :loading="isImageChecking"></spinner-indicator>
                        </div>


                        <div v-if="loadError" class="text-danger">
                            {{gettext("The URL doesn't refer to an image or the image is not publicly accessible.")}}
                        </div>

                    </div>
                </div>
                <div class="col" v-if="!loadError">
                    <button type="button"
                            class="btn btn-danger"
                            v-if="!isEmpty"
                            @click="removeImage"

                    >{{gettext('Remove image')}}
                    </button>
                </div>
            </div>


        </template>
    </form-accordion>

</template>

<script>
    import FieldWithErrors from './FieldWithErrors';
    import FormAccordion from './FormAccordion';
    import SpinnerIndicator from './SpinnerIndicator';
    import FileSelect from './forms/FileSelect';

    const defaultImage = '/static/site/img/no-image.gif';
    export default {
        components: {
            SpinnerIndicator,
            FieldWithErrors,
            FormAccordion,
            FileSelect
        },
        props: {
            formData: {
                required: true
            },
            visible: {
                required: false
            },
            serverErrors: {
                required: false,
                default: null
            },
<<<<<<< HEAD
            edit: {
                required: false,
                default: false
=======
            languages: {
                required: true
            },
            language: {
                required: true
>>>>>>> issue-495
            }
        },
        data() {
            return {
                visibleModel: this.visible,
                imageData: defaultImage,
                activeTab: this.edit ? 1 : 0,
                isImageChecking: false,
                imageCheckUrl: '',
                loadError: false,
                file: null
            };
        },
        computed: {
            isEmpty() {
                return this.imageData === defaultImage;
            },
            fileName() {
                if (this.imageData) {
                    const parts = this.imageData.split('/');
                    return parts[parts.length - 1]
                }
                return ''
            },
            imageUrl() {
                return this.formData.image_i18n.value;
            }

        },
        methods: {
            click(form) {
                this.$emit('click-field', form)
            },
            gettext(text) {
                return gettext(text);
            },
            imageProcess(ev) {
                this.loadError = false;
                this.isImageChecking = false;
                let input = ev.target;

                if (input.files && input.files[0]) {
                    this.formData.image_i18n.errors = null;
                    // store to value, it will be used to send as "new FormData()"
                    this.formData.image_upload.value = input.files[0];
                    this.formData.image_i18n.value = '';

                    let reader = new FileReader();
                    reader.onload = (e) => {
                        this.imageData = e.target.result;
                    };
                    reader.readAsDataURL(input.files[0]);
                    this.file = input.files[0];
                } else {
                    this.imageData = defaultImage;
                    this.file = null;
                }
            },
            removeImage() {
                this.loadError = false;
                if (this.formData.image_i18n.readonly) {
                    this.click(this.formData.image_i18n);
                }
                else {
                    this.imageData = defaultImage;
                    // empty image should be true empty to detect is it specified on the backend
                    this.formData.image_i18n.value = '';
                    this.formData.image_upload.value = null;
                    this.file = null;
                    this.resetFileInput();
                }
            },
            resetFileInput() {
                if (this.$refs.imageUpload) {
                    this.$refs.imageUpload.value = '';
                }
            },
            changeUrl(val) {
                this.resetFileInput();
                this.loadError = false;
                this.isImageChecking = true;
                this.formData.image_i18n.value = val;
            },
            loadImageError() {
                if (this.isImageChecking) {
                    this.isImageChecking = false;
                    this.loadError = true;
                }
            },
            loadImageSuccess() {
                this.loadError = false;
                if (this.isImageChecking) {
                    this.isImageChecking = false;
                }
            },
            changeTab(tab) {
                this.activeTab = tab;
                this.loadError = false;
            }
        },
        watch: {
            serverErrors(val) {
                if (val) {
                    this.visibleModel = this.visibleModel || val.image_i18n
                }
            },
            'formData.image_i18n.value'(val) {
                this.imageData = val ? val : defaultImage;
            }

        }
    }
</script>

<style lang="scss">
    .thumbnail {
        margin: 10px 0;
        img {
            max-height: 300px;
            max-width: 300px;
        }
    }

    .image-error {
        margin-bottom: 10px;
        font-size: 11px;
    }

    .well.well-sm {
        padding: 5px 0;
    }

</style>
