import Vue from 'vue'
import App from './App.vue'

import VueClipboard from 'vue-clipboard2';
import VeeValidate from 'vee-validate';
import VModal from 'vue-js-modal';
import VueKonva from 'vue-konva';
import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import axios from 'axios'

const settings = require('./settings.js')

axios.defaults.baseURL = settings.SERVER_URL;
axios.defaults.headers.post['Content-Type'] = 'multipart/form-data';
Vue.prototype.$axios = axios;

Vue.config.productionTip = false

Vue.use(VueClipboard);
Vue.use(VeeValidate);
Vue.use(VueKonva);
Vue.use(VueMaterial);
Vue.use(VModal, { 
  dynamic: true,
  dialog: true
});

new Vue({
  render: h => h(App),
}).$mount('#app')
