<template>
  <md-content>

    <md-card md-with-hover
      v-for="image in image_list"
      :key="image.id">

      <md-card-header>
        <h6 class="md-title">{{ image.label }}</h6>
      </md-card-header>

      <md-card-media md-ratio="16:9">
        <img 
          :src="image.src"
          :id="image.id"
          @click="handleClickCard"
        >
      </md-card-media>

      <md-card-actions>
        <button
          class="md-button"
          :id="image.id"
          @click="handleClickCard"
        >
          annotate
        </button>
      </md-card-actions>

    </md-card>

  </md-content>
</template>

<style scoped>
  .md-card {
    width: 300px;
    margin: 10px;
    display: inline-block;
    vertical-align: top;
  }
</style>

<script>
export default {
  name: 'ImagesBar',

  data() {
    return {
      clicked_image: null,
      local_image_list: null
    };
  },

  props: {
    image_list: {
      type: Array
    }
  },

  watch: {
    image_list() {}
  },

  methods: {
    handleClickCard(event){

      this.local_image_list = JSON.parse(localStorage.getItem('image_list'));
      let target_image = this.local_image_list.find(img => img.id === parseInt(event.target.id))

      this.clicked_image = new Image();
      this.clicked_image.id = parseInt(target_image.id);
      this.clicked_image.src = String(target_image.src);
      this.clicked_image.vertical_division = parseInt(target_image.vertical_division);
      this.clicked_image.rects_list = target_image.rects_list;
      this.clicked_image.label = String(target_image.label);

      // send clicked image info to workPanel
      this.$emit("inputData", this.clicked_image);
      this.clicked_image = null;

    }
  }
}
</script>
