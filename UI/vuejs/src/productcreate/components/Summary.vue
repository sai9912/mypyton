<template>
    <div v-if="formData">

        <fieldset>
            <legend data-v-84007da2="">{{ gettext('Summary') }}</legend>

            <product-summary :form-data="formData"
                             :response-data="responseData"
                             :package-level="packageLevel"
                             :gtin="gtin13"
                             :gtin14="gtin14"
                             :prefix="prefix"
                             :language="language"
                             :id="id"
                             :finish="true"
                             :package-type-name="packageTypeName"
                             :show-link="true"
            >

            </product-summary>
        </fieldset>
    </div>
</template>

<script>

    import ProductSummary from "../../common/components/Summary/ProductSummary"

    export default {
        components: {
            ProductSummary
        },
        data() {
            return {
                formData: null,
                packageLevel: 0,
                gtin13: '',
                gtin14: '',
                prefix: '',
                language: '',
                id: '',
                packageTypeName: ''
            }
        },
        mounted() {
            const productStoreState = this.$store.state.ProductCreation;
            if(!productStoreState.summaryData) {
                this.$router.push('/');
                return;
            }
            this.formData = productStoreState.summaryData.formData;
            this.responseData = productStoreState.summaryData.result;
            this.packageLevel = productStoreState.packageLevel;
            this.gtin13 = productStoreState.summaryData.result.gtin.value.substring(1, 14);
            this.gtin14 = productStoreState.summaryData.result.gtin.value.substring(0, 14);
            this.prefix = productStoreState.summaryData.result.gs1_company_prefix.value;
            this.language = productStoreState.language || 'en';
            this.id = productStoreState.summaryData.result.id.value;
            const packageType = productStoreState.packageTypeList.find((type) => type.id == productStoreState.packageType);
            this.packageTypeName = packageType && packageType.name[this.language];
        },
        methods:{
            gettext(text) {
                return gettext(text);
            },
        }
    }
</script>

<style scoped>

</style>

