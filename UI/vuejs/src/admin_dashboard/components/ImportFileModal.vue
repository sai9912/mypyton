<template>
    <b-modal id="import_modal" v-model="opened" class="activate-prefix-modal" @hidden="onModalClose()">
        <div slot="modal-header" class="container-fluid">
            <button type="button" class="close" @click.prevent="opened = false">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{{ gettext('Close') }}</span>
            </button>
            <h4 class="modal-title" id="ProductDeleteTitle">{{ title }}</h4>
        </div>

        <div class="row">
            <div class="col-12">
                <p>{{ gettext('Please select an .xlsx file to upload.') }}</p>
                <p>
                    <b-form-file
                        v-model="import_file"
                        :state="Boolean(import_file)"
                        ref="input_file"
                        accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                        placeholder="Choose a file...">
                    </b-form-file>
                </p>

                <div v-if="api_response && api_response.upload_details">
                    <p>
                        <span class="text-success">{{ gettext('Success count') }}: {{ api_response.upload_details.success_count }}</span><br>
                        <span class="text-danger">{{ gettext('Error count') }}: {{ api_response.upload_details.error_count }}</span>
                    </p>

                    <div v-if="api_response.upload_details.errors && api_response.upload_details.errors.length !== 0" class="messages">
                        <h6>{{ gettext('Error messages') }}:</h6>
                        <p class="message" v-for="error in api_response.upload_details.errors">
                            Row #{{ error.row_id }}<br>
                            <template v-for="(field_errors, field_name) in error.error_messages">
                                {{ field_name }}:<br>
                                <template v-for="field_error in field_errors">{{ field_error }}<br></template>
                            </template>
                        </p>
                    </div>
                </div>

                <div v-if="api_response && api_response.server_errors">
                    <p class="text-danger" v-for="error in api_response.server_errors">
                        {{ error }}
                    </p>
                </div>
            </div>
        </div>

        <div slot="modal-footer" class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <button @click.prevent="$root.$emit('bv::hide::modal','import_modal')" type="button" class="btn btn-info" data-dismiss="modal">
                        {{ gettext('Cancel') }}
                    </button>

                    <b-button
                        @click.prevent="upload"
                        :disabled="!import_file"
                        variant="primary"
                        class="float-right">
                        {{ gettext ('Upload')}}
                    </b-button>
                </div>
            </div>
        </div>
    </b-modal>
</template>

<script>

export default {
    data() {
        return {
            opened: false,
            title: gettext('Data Import'),
            import_file: null,
            api_field_name: 'import_file',
            api_response: null,
        };
    },
    methods: {
        gettext(text) {
            return gettext(text);
        },
        open(title, api_url) {
            this.opened = true;
            this.title = title;
            this.api_url = api_url;
        },
        upload() {
            let submit_data = new FormData();
            submit_data.set(this.api_field_name, this.import_file);
            this.$http.put(this.api_url, submit_data).then(
                response => {
                    console.log(response.body);
                    this.api_response = response.body;
                },
                response => {
                    console.log('APIError:', response);
                    this.api_response = {
                        server_errors: response.body
                    };
                }
            );
        },
        onModalClose() {
            this.opened = false;
            this.api_url = null;
            this.api_response = null;
            this.$refs.input_file.reset();
            this.title = gettext('Data Import')
        },
    },
    props: {},
    components: {},
}
</script>

<style lang="scss">
    .activate-prefix-modal {
        overflow-y: hidden
    }
    div.messages {
        max-height: 200px;
        overflow-y: scroll;
    }
</style>
