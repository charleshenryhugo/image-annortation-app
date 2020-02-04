<template>
  <div id="app">
    <div class="md-layout md-gutter md-alignment-center">
      <md-content
        class="md-layout-item md-size-30 md-scrollbar"
        v-bind:style="{ 'max-height' : max_height}"
      >
        <images-bar
          @inputData="getClickedImage" 
          :image_list="image_list"
        />

        <md-button
          class="md-raised md-primary"
          @click="$modal.show('taskRegisterModal')"
          style="font-weight: 900; font-size: 15px;"
        >
          Create New Task
        </md-button>
        <md-button
          class="md-raised md-primary"
          @click="downloadTaskJsonByCode"
          v-if="!!image_list"
        >
          get json
        </md-button>

      </md-content>

      <md-content
        class="md-layout-item md-size-70 md-scrollbar"
        v-bind:style="{ 'max-height' : max_height}"
      >
        <workPanel
          :initial_image="initial_image" 
          :selected_image="clicked_image"
        />

      </md-content>
    </div>

    <taskRegisterModal/>

  </div>
</template>

<script>
import taskRegisterModal from './components/TaskRegisterModal.vue';
import workPanel from './components/WorkPanel.vue';
import imagesBar from './components/ImagesBar.vue';
import { saveAs } from 'file-saver'

const settings = require('./settings.js');

export default {
  name: 'app',
  components: {
    workPanel,
    imagesBar,
    taskRegisterModal
  },
  data() {
    return {
      initial_image: null,
      clicked_image: null,
      cur_task_code: null,
      image_list: null,
      max_height: `${window.innerHeight}px`
    };
  },

  mounted() {
    this.$nextTick(function() {
      // window resize event listener
      window.addEventListener('resize', this.updateClass)

      // parse request url /tasks/xxxxxxxxxx
      let url = window.location.pathname;

      // check request url, only /tasks/xxxxxxxxxx pass
      if (url.match(settings.CLIENT_REQUEST_PATH_MODE)) {
        // parse task_code
        this.cur_task_code = url.slice(-10);

        // fetch api and update localStorage
        this.fetchImageListByCode();

      } else {
        // request path wrong, render taskRegisterModal
        this.$modal.show('taskRegisterModal');
      }

      // end for mounted

    });

  },

  methods: {
    getClickedImage(variable) {
      this.clicked_image = variable;
    },

    serveInitialImage() {
      // send the initial image to workPanel
      this.initial_image = new Image();
      this.initial_image.id = parseInt(this.image_list[0].id);
      this.initial_image.src = String(this.image_list[0].src);
      this.initial_image.label = this.image_list[0].label;
      this.initial_image.vertical_division = parseInt(this.image_list[0].vertical_division);
      this.initial_image.rects_list = this.image_list[0].rects_list;
    },

    // fetch image list from server by taskCode
    fetchImageListByCode() {
      
      // call API
      this.$axios.get( '/api/task', {
        params: {
          task_code: this.cur_task_code
        }
      })
      .then(response => {

        // eslint-disable-next-line
        console.log(response.data);

        let task_images = response.data['images'];
        task_images.task_name = response.data['task'];

        // TODO modify image src
        task_images.forEach(img => {
          img.src = settings.SERVER_URL + img.src;
          img.rects_list = img.rects_list.length === 0 ? [] : JSON.parse(img.rects_list);
        });

        // put new fetched images into localStorage
        localStorage.setItem('image_list', JSON.stringify(task_images));

        // update this.image_list
        this.image_list = task_images;

        // send the initial image to workPanel
        this.serveInitialImage();
        
        // eslint-disable-next-line
        console.log('new image_list loaded !!');

      })
      .catch(error => {
        if (error.response) {

          // show task register modal if 404 NOT FOUND
          if (error.response.status === 404) {
            this.$modal.show('taskRegisterModal');
          }

        } else {
          // eslint-disable-next-line
          console.log('Error', error.message)
        }
      })
      .finally(() => {
      });

    },

    // fetch task json data from server by taskcode 
    downloadTaskJsonByCode() {
      // call API
      this.$axios.get( '/api/task/download', {
        params: {
          task_code: this.cur_task_code
        }
      })
      .then(response => {

        // eslint-disable-next-line
        console.log(response.data);

        let file_name = `${response.data.task}.json`;
        let file_to_save = new Blob( [JSON.stringify(response.data, undefined, 2)], {
          type: 'application/json',
          name: file_name
        });
        saveAs(file_to_save, file_name);

      })
      .catch(error => {
        if (error.response) {
          // eslint-disable-next-line
          console.log('Error', error);

        } else {
          // eslint-disable-next-line
          console.log('Error', error.message);

        }
      })
      .finally(() => {
      });
    },

    updateClass() {
      this.max_height = `${window.innerHeight}px`;
    }

  }
}
</script>

<style scoped>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  vertical-align: middle;
  margin-top: 60px;
}
.md-content {
  max-height: 600px;
  overflow: auto;
}
</style>
