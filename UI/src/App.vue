<template>
    <div id="app">
        <router-view v-title/>
    </div>
</template>

<script>
    export default {
        name: "app"
    };
</script>

<style lang="scss">
    @import "~bootstrap/dist/css/bootstrap.css";
    @import "~bootstrap-vue/dist/bootstrap-vue.css";

    @import '../static/site/css/master.css';
      @import '../static/site/css/style.css';
      @import '../static/site/css/style_bs4.css';

    html {
        height: 100%;
    }

    #app,
    body {
        height: 100%;
    }

    .container {
        width: 1100px;
    }

    .panel {
        margin-bottom: 20px;
        background-color: #ffffff;
        border: 1px solid transparent;
        -webkit-box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
        box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
        border-radius: 0;
    }

    .panel-default {
        border: 2px solid #888b8d;
    }

    .panel-primary {
        border-color: #002c6c;
    }

    .panel .table th {
        border-top: none;
    }

    .panel-primary > .panel-heading,
    .panel-default > .panel-heading {
        font-size: 16px;
        padding: 7px 15px;
    }

    .panel-primary > .panel-heading {
        color: #fff;
    }

    .breadcrumb-item.active,
    .breadcrumb-item + .breadcrumb-item::before {
        color: #fff;
    }

    .well-sm {
        padding: 9px;
    }

    .well {
        min-height: 20px;
        padding: 19px;
    }

    .btn-primary.disabled,
    .btn-primary:disabled {
        background-color: #002c6c;
        border-color: #002c6c;
    }

    .panel-table-container {
        margin: 0px -15px;
    }

    .dropdown-menu {
        padding: 0;
    }

    .dropdown-item {
        outline: none;
        padding: 0.5rem 1.5rem;
    }

    .dropdown-item:hover,
    .dropdown-item:focus {
        background-color: #eaebec;
    }

    .v-select .dropdown-toggle {
        display: flex !important;
        flex-wrap: wrap;
    }

    .v-select input[type="search"],
    .v-select input[type="search"]:focus {
        flex-basis: 20px;
        flex-grow: 1;
        height: 33px;
        padding: 0 20px 0 10px;
        width: 100% !important;
    }

    .v-select li > a {
        padding: 5px 20px;
    }

    .accent-link {
        color: #f26334;
        &:hover {
            color: #bb4e2a;
        }
    }
</style>
