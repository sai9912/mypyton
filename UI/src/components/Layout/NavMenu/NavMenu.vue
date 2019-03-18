<template>
  <nav class="site-nav col">
    <ul>
      <li>
        {{ $t('My Account') }}
        <ul>
          <li>
            <router-link to="/dashboard"> {{ $t('Dashboard') }}</router-link>
          </li>
          <li>
            <router-link to="/prefixes"> {{ $t('Prefix management') }}</router-link>
          </li>
          <li>
            <a href="https://attendee.gotowebinar.com/recording/7198145658454918404">
              {{ $t('Training and Resources') }}
            </a>
          </li>
        </ul>
      </li>
      <li>
        {{ $t('Product Manager') }}
        <ul>
          <li>
            <router-link to="/products">{{ $t('My Products') }}</router-link>
          </li>
          <li>
            <router-link to="/products/export"> {{ $t('Export Products') }}</router-link>
          </li>
          <li>
            <router-link to="/products/import"> {{ $t('Import Products') }}</router-link>
          </li>
        </ul>
      </li>
    </ul>


    <active-prefix>

    </active-prefix>


    <div class="clearfix"></div>
  </nav>
</template>

<script>
  import ActivePrefix from './../../Prefixes/ActivePrefix/ActivePrefix'
  export default {
    name: 'nav-menu',
    components: {
      ActivePrefix
    }
  }
</script>

<style scoped>
  nav.site-nav {
    max-width: 200px;
  }

  nav.site-nav > ul > li > ul > li > a.router-link-active {
    color: #f26334;
  }


</style>
