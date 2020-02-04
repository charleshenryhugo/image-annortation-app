<template>
  <modal
    name="taskRegisterModal"
    transition="nice-modal-fade"
    :pivot-y="0.5"
    :adaptive="true"
    :scrollable="true"
    :reset="true"
    width="60%"
    height="auto"
  >
    <div class="partition-title">
      Create New Annotation Task
    </div>

    <md-list class="md-dense">
      <md-list-item class="md-layout md-alignment-center">

          <md-field class="md-layout-item md-size-50">

            <label>task name</label>
            <md-input 
              v-model="task_name"
              placeholder="input task name"
              type="text" name="task_name_field" v-validate="'required'"
            />
            <span class="md-error" v-if="errors.has('task_name_field')" style="opacity:1; color:red;">
              task name is required
            </span>
          </md-field>

          <md-field class="md-layout-item md-size-30">

            <label>divide (integer)</label>
            <md-input 
              type="number" name="vertical_division_field" v-validate="'numeric|required'"
              v-model="vertical_division" placeholder="vertical divide"
            />
            <span class="md-error" v-if="errors.has('vertical_division_field')" style="opacity:1; color:red;">
              positive vertical divide number is required
              </span>

          </md-field>

      </md-list-item>

      <md-list-item 
        v-for="image in image_list" :key="image.key"
        class="md-layout md-alignment-center"
      >
          <md-field class="md-layout-item md-size-20">

            <label>label</label>
            <md-input
              type="text" :name="`image-label-${image.key}`" v-validate="'required'"
              v-model="image.label" placeholder="label"
            />
            <span class="md-error" v-if="errors.has(`image-label-${image.key}`)" style="opacity:1; color:red;">
              label is required
            </span>
          </md-field>

          <md-field class="md-layout-item md-size-30">

            <input
              type="file" :name="`image-${image.key}`" v-validate="'image|required'"
              @change="onFileChanged"
              :id="image.key"
            >
            <span class="md-error" style="opacity:1; color:red;">
              {{ errors.first(`image-${image.key}`) }}
            </span>

          </md-field>

          <md-field class="md-layout-item md-size-20">

            <md-avatar class="md-large">
              <img 
                :src="image.src"
                :id="image.key"
                v-if="!!image.file"
              />
            </md-avatar>
          </md-field>

          <md-field class="md-layout-item md-size-15">

            <button
              class="md-button md-raised"
              @click="removeThisItem"
              :id="image.key"
            >
              del
            </button>

          </md-field>

      </md-list-item>
    </md-list>

    <div class="md-layout md-alignment-center">
      <div class="md-layout md-alignment-left">

        <md-button
          class="md-raised md-primary" 
          @click="submitItems"
        >
          submit
        </md-button>

        <md-button 
          class="md-fab md-dense md-raised" 
          @click="addItem"
        >
          <md-icon> + </md-icon>
        </md-button>

        <span
          v-if="image_list===null || image_list.length===0" 
          style="color:green;"
        >
          please add at least one image
        </span>

      </div>

      <md-button class="md-raised" @click="clearItems">
        clear
      </md-button>

      <md-button class="md-raised" @click="closeModal">
        close
      </md-button>

    </div>

    <md-snackbar :md-active.sync="sending">sending...</md-snackbar>
    <md-snackbar :md-active.sync="task_saved">task saved !!</md-snackbar>

    <v-dialog/>

  </modal>
</template>

<script>
  const settings = require('../settings.js');

  export default {
    name: 'taskRegisterModal',
    data () {
      return {
        vertical_division: null,
        task_name: null,
        image_list: null,
        sending: false,
        task_saved: false
      };
    },

    mounted() {
      this.image_list = [this.blankImage()];
      // console.log(this.image_list);
    },

    methods: {
      addItem() {
        if (this.image_list.length === 0) {
          this.image_list = [this.blankImage()];
        } else {
          let new_image = this.blankImage();
          new_image.key = String( parseInt(this.image_list.slice(-1)[0].key) + 1 );
          this.image_list.push(new_image);
        }
      },

      onFileChanged (event) {
        let files = event.target.files;
        if (! (files && files[0])) { 
          return; 
        }

        // by default, set label to the file name, remove the ext.
        this.image_list.find(img => img.key === event.target.id).label = files[0].name.replace(/\.[^/.]+$/, '');

        // put selected image into image_list
        this.image_list.find(img => img.key === event.target.id).file = files[0];

        // image preview
        let reader = new FileReader();

        reader.onload = (e) => {
          this.image_list.find(img => img.key === event.target.id).src = e.target.result;
        };
        reader.readAsDataURL(files[0]);

      },

      clearItems() {
        this.vertical_division = null;
        this.task_name = null;
        this.image_list = [];
      },

      closeModal() {
        this.$modal.hide('taskRegisterModal');
      },

      removeThisItem(event) {
        // rm from this.image_list
        this.image_list = this.image_list.filter(
          img => img.key !== event.target.id
        );
      },

      blankImage() {
        return {
          key: '0',
          file: null,
          src: null,
          label: '',
          valid: false
        }
      },

      submitItems() {

        // do validation before submit
        this.$validator.validateAll().then(result => {
          if (result) {

            // eslint-disable-next-line
            console.log('validation success');

            // return if no images in image_list
            if (this.image_list === null || this.image_list.length === 0) {

              // eslint-disable-next-line
              console.log('no images to submit');
              return;
            }

            // form request data
            let formData = new FormData();
            formData.append('task_name', this.task_name)
            formData.append('vertical_division', this.vertical_division);

            this.image_list.forEach( function(img) {
              // always append image type: jpeg, png, etc.
              img.label = `${img.label}.${img.file.type.slice(6)}`;

              formData.append(img.label, img.file);
            });

            // start to send POST request
            this.sending = true
            this.$axios.post( '/api/task/register/upload/',
              formData,
            )
            .then(response => {
              this.task_saved = true;

              // eslint-disable-next-line
              console.log(response.data);

              // POST success, show new task link in dialog to user
              this.showTaskLinkDialog(response.data);
            })
            .catch(error => {
              if (error.response) {
                // eslint-disable-next-line
                console.log(error.response);

                this.showErrorsDialog(error);
              } else {
                this.showErrorsDialog(error);
              }
            })
            .finally(() => {
              this.sending = false;
            });

          }
        });
      },

      showTaskLinkDialog (data) {
        // TODO
        let task_link = `${settings.CLIENT_URL}/tasks/${data.task_code}`;

        this.$modal.show('dialog', {
          title: `new task created: ${data.task_name}`,

          text: 'Check your new task by the following link:<br/>' +
                `<a href="${task_link}">${task_link}</a>`,

          buttons: [
            {
              title: 'COPY LINK',
              handler: () => {
                this.$copyText(task_link).then((e) => {
                  // eslint-disable-next-line
                  console.log(e);
                });
              }
            },
            {
              title: 'CLOSE',
              handler: () => {
                this.$modal.hide('dialog');
              }
            }
          ]
        });
      },
      showErrorsDialog (data) {
        this.$modal.show('dialog', {
          title: 'ERROR POSTING', 
          text: JSON.stringify(data)
        });
      }
    }
  }
</script>

<style scoped>
  .partition-title {
    padding: 20px;
    text-align: center;
    letter-spacing: 1px;
    font-size: 20px;
  }
</style>