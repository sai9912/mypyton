<template>
  <div
    class="ladda-block"
    :class="{'ladda-block--shake': animated}"
  >
    <button class="btn btn-primary ladda-button"
            ref="ladda"
            :data-style="dataStyle"
            :type="buttonType"

            @click="handleClick">
      <span class="ladda-label"><slot>Submit</slot></span>
    </button>
  </div>
</template>

<script>
  import {create} from 'ladda'

  export default {
    name: 'VueLadda',
    props: {
      'dataStyle': {
        type: String,
        default: 'expand-left'
      },
      loading: {
        type: Boolean,
        required: true
      },
      error: {
        type: Object
      },
      progress: {
        validator: function (progress) {
          return progress >= 0 && progress <= 1
        },
        default: 0
      },
      buttonType: {
        type: String,
        default: 'button'
      }
    },
    data() {
      return {
        animated: false
      }
    },
    watch: {
      loading: function (loading) {
        loading ? this.ladda.start() : this.ladda.stop()
      },
      error: function () {
        if (this.error) {
          this.animated = true
          setTimeout(() => {
            this.animated = false
          }, 1000)
        }
      },
      progress: function (progress) {
        this.ladda.setProgress(progress)
      }
    },
    methods: {
      handleClick: function (e) {
        this.$emit('click', e)
      }
    },
    mounted: function () {
      this.ladda = create(this.$refs.ladda)
      this.loading ? this.ladda.start() : this.ladda.stop()
    },
    beforeDestroy: function () {
      this.ladda.remove()
      delete this.ladda
    }
  }
</script>

<style>
  @import '~ladda/dist/ladda-themeless.min.css';

  .ladda-block {
    display: inline-block;
  }

  .ladda-block--shake {
    transition-property: translate3d;
    animation: shake 0.82s cubic-bezier(.36, .07, .19, .97) both;
    transform: translate3d(0, 0, 0);
    backface-visibility: hidden;
  }

  @keyframes shake {
    10%, 90% {
      transform: translate3d(-1px, 0, 0);
    }

    20%, 80% {
      transform: translate3d(2px, 0, 0);
    }

    30%, 50%, 70% {
      transform: translate3d(-4px, 0, 0);
    }

    40%, 60% {
      transform: translate3d(4px, 0, 0);
    }
  }
</style>
