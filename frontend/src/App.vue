<template>
  <div id="app">

    <bg style="width: 100%;height:100%;position: absolute;z-index:-100;buttom:0" />
    <div>
      <b-navbar toggleable="lg" type="light" variant="light">
        <b-navbar-brand to="/" href="#">
          <img src="./assets/logo_transparent.png" class="d-inline-block align-top">
          LicenseRec
        </b-navbar-brand>
        <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
        <b-collapse id="nav-collapse" is-nav>
          <b-navbar-nav>
            <b-nav-item @click="enter_rec">Choose a license</b-nav-item>
            <b-nav-item to="/query">Compatibility query</b-nav-item>
            <!-- <b-nav-item to="/">Guide</b-nav-item>
            <b-nav-item to="/">About</b-nav-item> -->
          </b-navbar-nav>
          <b-navbar-nav class="ms-auto">
            <b-nav-item-dropdown right>
              <!-- <template #button-content>
                <em>User</em>
              </template>
              <b-dropdown-item href="#">Profile</b-dropdown-item>
              <b-dropdown-item href="#">Sign Out</b-dropdown-item> -->
            </b-nav-item-dropdown>
           
          </b-navbar-nav>
        </b-collapse>
      </b-navbar>
    </div>
    <div class="center-page" style="background-color:rgba(0,0,0,0);">
      <router-view></router-view>
    </div>
    <div id="app-footer" style="font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;">
      <hr class="my-4" />
      © Copyright 2022
      <b-link href="https://osslab-pku.github.io/" target="_blank">OSS Lab</b-link>, Peking University. All rights reserved.<br />
      Maintained by
      <b-link href="https://zhcxww.github.io/" target="_blank">Weiwei Xu</b-link>.<br />
      The content of this site, all source code and data available are licensed under the
      <b-link href="https://spdx.org/licenses/MulanPSL-2.0.html" target="_blank"> Mulan PSL v2</b-link>.
    </div>

  </div>
</template>

<script>
import bg from "@/components/bg";
export default {
  name: 'App',
  components: {
    bg
  },

  methods: {
    enter_rec() {
      this.$router.push('rec');
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;

}

#center-page {
  margin-top: 30px;
  margin-bottom: 30px;
  margin-right: 5%;
  margin-left: 5%;
  position: relative;
}

#app-footer {
  text-align: center;
  margin-right: 5%;
  margin-left: 5%;
  margin-top: 120px;
  margin-bottom: 30px;
  position: relative;
  background-color:rgba(0,0,0,0)
}
</style>
