<template>
  <div class="page-title">
    <h2>
      {{$t($pageTitle)}}
    </h2>
    <div class="help-link">
      <a href="https://attendee.gotowebinar.com/recording/7198145658454918404">
        <img src="/static/site/img/training_button_2.png" alt="Training"
             style="width: auto;height: 30px;">
      </a>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'page-title'
  }
</script>

<style scoped>
  .page-title h2{
    padding: 10px 20px;
  }
  .help-link {
    position: absolute;
    right: 10px; top: 10px;
    text-align: right;
  }
</style>
