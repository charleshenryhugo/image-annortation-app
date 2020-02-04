<template>
  <md-card>

    <md-card-header>
      <h5 class="md-title">{{ cur_image.label}}</h5>
    </md-card-header>

    <md-card-media>
      <v-stage ref="stage" 
        @mousemove="handleMouseMoveOnStage" 
        v-bind:config="stageSize"
        align="center"
      >
        <v-layer ref="imglayer">
          <v-image
            @mousemove="handleMouseMoveOnImage"
            @click="handleClickImage"
            :config="{
                image: cur_image,
                x: image_offset.x,
                y: image_offset.y,
            }"
          ></v-image>
        </v-layer>
        <v-layer ref="rectslayer">
          <v-rect
            @click="handleClickImage"
            :config="{
              x: float_rect.x, 
              y: float_rect.y, 
              width: float_rect.width, 
              height: float_rect.height, 
              stroke: 'green'
            }"
          ></v-rect>
          <v-rect
            @click="handleClickRect"
            v-for="rect in rects_list"
            :key="rect.id"
            :config="{
              x: rect.x, 
              y: rect.y, 
              width: rect.width, 
              height: rect.height, 
              stroke: 'blue',
            }"
          ></v-rect>
        </v-layer>
      </v-stage>
    </md-card-media>

    <md-card-actions>

      <md-button 
        class="md-raised md-primary"
        style="font-weight: 900;"
        @click="handleClickSave"
        v-if="cur_image.height>0 && cur_image.width>0"
      >
        save this
      </md-button>

      <md-button> {{ mousePos }} </md-button>

    </md-card-actions>

    <md-snackbar :md-active.sync="saved">
      Saved with success !!
    </md-snackbar>

  </md-card>
</template>

<script>
export default {

  props: {
    initial_image: {
      type: Image
    },
    selected_image: {
      type: Image
    }
  },

  data() {
    return {
      stageSize: { 
        width: window.innerWidth * 0.6,
        height: window.innerHeight * 0.8
      },
      image_offset: {x: 0, y: 0},
      cur_image: null,
      mousePos: null,
      rects_list: [],
      float_rect: { x: 0, y: 0, width: 0, height: 0 },
      sending: false,
      saved: false
    };
  },

  watch: {
    initial_image() {
      this.initial_image.onload = () => {
        this.cur_image = this.initial_image;
        this.rects_list = this.cur_image.rects_list;
        this.cur_image.rect_height = Math.floor(this.cur_image.height / this.cur_image.vertical_division);
        
        // resize stage size to match cur_image
        this.updateStageSize();
      }
    },

    selected_image() {
      // clicks on ImagesBar
      this.selected_image.onload = () => {
        // save the current image annotation before switching to the next one
        this.localSave();

        // clear current float rect
        this.float_rect = { x: 0, y: 0, width: 0, height: 0 };

        this.cur_image = this.selected_image;
        this.rects_list = this.cur_image.rects_list;
        this.cur_image.rect_height = Math.floor(this.cur_image.height / this.cur_image.vertical_division);

        // resize stage size to match cur_image
        this.updateStageSize();
      }
    }
  },

  created() {
    this.cur_image = new Image();
  },

  methods: {
    updateStageSize() {
      this.stageSize.width = this.cur_image.width + this.cur_image.rect_height;
      this.stageSize.height = this.cur_image.height + this.cur_image.rect_height;
    },

    handleMouseMoveOnStage(event) {
      // mouse position changes
      const mousePos = event.target.getStage().getPointerPosition();
      const x = mousePos.x - this.image_offset.x;
      const y = mousePos.y - this.image_offset.y;
      this.mousePos = "x: " + parseInt(x) + ", y: " + parseInt(y);
    },
    handleMouseMoveOnImage(event) {
      // green rect float
      const mousePos = event.target.getStage().getPointerPosition();
      const side_len = this.cur_image.rect_height;

      this.float_rect = {
        x: side_len * Math.floor((mousePos.x - this.image_offset.x) / side_len) + this.image_offset.x,
        y: side_len * Math.floor((mousePos.y - this.image_offset.y) / side_len) + this.image_offset.y,
        width: side_len - 2,
        height: side_len - 2
      };
    },
    handleClickImage(event) {
      // when clicked on green float rect
      // blue rect selected
      const mousePos = event.target.getStage().getPointerPosition();
      const side_len = this.cur_image.rect_height;

      var rect = {
        x: side_len * Math.floor((mousePos.x - this.image_offset.x) / side_len) + this.image_offset.x,
        y: side_len * Math.floor((mousePos.y - this.image_offset.y) / side_len) + this.image_offset.y,
        width: side_len - 2,
        height: side_len - 2
      };
      this.rects_list.push(rect);

      this.localSave();

    },
    handleClickRect(event) {
      // blue rect disappeared while clicked
      const mousePos = event.target.getStage().getPointerPosition();
      const side_len = this.cur_image.rect_height;

      const click_x = side_len * Math.floor((mousePos.x - this.image_offset.x) / side_len) + this.image_offset.x;
      const click_y = side_len * Math.floor((mousePos.y - this.image_offset.y) / side_len) + this.image_offset.y;

      this.rects_list = this.rects_list.filter(
        rect => !(rect.x === click_x && rect.y === click_y)
      );

      this.localSave();

    },
    handleClickSave() {

      // save to server
      this.globalSave();

    },

    localSave() {

      // save to localStorage
      let image_list = JSON.parse(localStorage.getItem('image_list')) || [];

      image_list.find(img => img.id === parseInt(this.cur_image.id)).rects_list = this.rects_list;
      localStorage.setItem('image_list', JSON.stringify(image_list));

      // eslint-disable-next-line
      console.log("saved locally");

    },

    // save updated rects_list to server
    globalSave() {

      // call API
      let formData = new FormData();
      formData.append('image_id', parseInt(this.cur_image.id));
      formData.append('rects_list', JSON.stringify(this.rects_list));

      // start to send POST request
      this.sending = true
      this.$axios.post( '/api/image/',
        formData,
      )
      .then(response => {
        this.saved = true;
        // eslint-disable-next-line
        console.log(response.data)
      })
      .catch(error => {
        if (error.response) {
          // eslint-disable-next-line
          console.log('Error', error.response);
        } else if (error.request) {
          // eslint-disable-next-line
          console.log('Error', error.request)
        } else {
          // eslint-disable-next-line
          console.log('Error', error.message)
        }
      })
      .finally(() => {
        this.sending = false;
      });

    }
  }
};
</script>
