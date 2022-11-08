<template>
  <div id="page">
    <div class="steps">
      <el-steps :active="step_active" align-center finish-status="success">
        <el-step title="Compatibility Check"></el-step>
        <el-step title="Preferences"></el-step>
        <el-step title="Term Comparison"></el-step>
      </el-steps>
    </div>

    <div id="main" class="main">
      <el-row :gutter="20" style="margin-top: 20px; height: 500px">
        <el-col :span="17">
          <div class="file_box">
            <div>
              <el-card style="height: 500px;">
                <div slot="header" class="clearfix">
                  <span style="font-size: 20px;color:white">License Compatibility Check</span>
                </div>
                <div class="file-url" v-loading="loading">
                <p style="font-size: 17px; font-weight:400;">You can upload your project or input Github repository url</p>
                <el-upload class="avatar-uploader" id="uploader" ref="uploader" action="#" :show-file-list="true"
                  :on-success="handleAvatarSuccess" :before-upload="beforeAvatarUpload" :on-change="file_change" :before-remove="remove_file"
                  :limit=1 accept=".rar,.zip" drag :auto-upload="false" :disabled="upload_disabled">
                  
                  <i class="el-icon-upload" style="color: #095da7"></i>
                  <div class="el-upload__text">Drag the file here, or <em>click to upload</em></div>
                  <div class="el-upload__tip" slot="tip">Only <strong>zip/rar</strong> files can be uploaded</div>
                </el-upload>
                <el-divider></el-divider>
                
                <div class="giturl">
                    <span style="display: inline; font-size: 20px">https://github.com/</span>
                    <b-form-input v-model="git_address.username" :disabled="git_disabled" 
                    placeholder="Username"
                    @change="git_change" style="width: 200px; display: inline"></b-form-input>
                    <span style="display: inline; font-size: 20px">/</span>
                    <b-form-input v-model="git_address.reponame" :disabled="git_disabled" 
                    placeholder="Repository name"
                    @change="git_change" style="width: 200px; display: inline"></b-form-input>
                </div>
                </div>
                <div class="description" id="description" style="display: none">
                <span>The licenses in the project</span>
                <el-divider></el-divider>
                <div style="overflow-y:scroll; height: 350px;">
                <!-- <b-popover target="AGPL-3.0-only" triggers="hover" disabled="true"><span style="color:cornflowerblue">MigrationHelperFrontend-master/MigrationHelperFrontend-master/test1</span><span>:MIT</span></b-popover> -->

                <div v-for="(file, index) in check_res.licenses_in_files" style="text-align: left; margin: 10px">
                  <div>
                  <i class="el-icon-warning"></i><span class="file-path">{{index}}:</span>
                  <span v-for="license in file">
                    <span  :id="license">{{license}},&nbsp</span>
                    <!-- <b-popover :target="license" triggers="hover" disabled="true"></b-popover> -->
                  </span>
                  </div>
                </div>
                </div>
                </div>
                <div>
                <router-view name="second" id="questions" style="display: none"></router-view>
                </div>
              </el-card>
            </div>
          </div>
        </el-col>
        <el-col :span="7">
          <div class="list">
            <el-card style="height: 500px">
              <div slot="header" class="clearfix">
                <span style="font-size: 20px;color:white">Recommendation List</span>
              </div>
              <div class="dropdown">
                <el-select v-model="cur_option" placeholder="Please choose">
                  <el-option v-for="item in sort_options" :key="item.value" :label="item.label" :value="item.value">
                  </el-option>
                </el-select>
              </div>
              <!-- <div v-for="license in licenses" :label="license" :key="license" >
                <ul>
              <el-radio>{{license}}</el-radio>
                </ul> -->
              <!-- <el-checkbox-group v-model="licenses" >
                  <el-checkbox v-for="license in licenses" :label="license" :key="license" style="display: block; float: left">{{license}}</el-checkbox>
                </el-checkbox-group> -->
              <el-table :data="table_data" style="overflow-y: scroll; height: 360px">
                <el-table-column label="Compatibility" width="70" >
                  <template slot-scope="scope">
                    <div class="circle"></div>
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="Name" width="200"></el-table-column>
              </el-table>
              <!-- </div> -->

            </el-card>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="18">
          <b-button type="primary" @click="upload_file_or_url">Start check</b-button>
          <b-button type="primary" >Skip this step</b-button>
          <b-button type="primary" @click="enter_questions" style="display: none">Next step</b-button>
          <b-button type="primary" @click="show_confict_depend_dict">test</b-button>
        </el-col>
        <el-col :span="6">

        </el-col>
      </el-row>
      <!-- <el-row>
        <el-col :span="24">
          <div style="margin-top: 20px; background: azure; height: 100px">开源许可证说明</div>
        </el-col>
      </el-row> -->
      
    </div>
  </div>

</template>

<script>
import $ from 'jquery'
export default {
  name: 'rec',
  data() {
    return {
      step_active: 0,
      licenses: [["MIT"], [ "GPL-2.0-only", "LGPL-2.1-or-later", "BSL-1.0", "Apache-2.0", "GPL-2.0-or-later"], ["LicenseRef-scancode-wordnet", "LicenseRef-scancode-public-domain", "LicenseRef-scancode-other-permissive", "LicenseRef-scancode-mit-old-style"]],
      table_data: [
        {compatibility: 0,name: 'MIT'},
        {compatibility: 0,name: 'Apache-2.0'},
        {compatibility: 0,name: 'GPL-3.0-only'},
        {compatibility: 0,name: 'BSD-3-Clause'},
        {compatibility: 0,name: 'GPL-2.0-only'},
        {compatibility: 0,name: 'AGPL-3.0-only'},
        {compatibility: 0,name: 'MPL-2.0'},
        {compatibility: 0,name: 'LGPL-3.0-only'},
        {compatibility: 0,name: 'BSD-2-Clause'},
        {compatibility: 0,name: 'Unlicense'},
        {compatibility: 0,name: 'ISC'},
        {compatibility: 0,name: 'EPL-1.0'},
        {compatibility: 0,name: 'CC0-1.0'},
        {compatibility: 0,name: 'LGPL-2.1-only'},
        {compatibility: 0,name: 'WTFPL'},
        {compatibility: 0,name: 'Zlib'},
        {compatibility: 0,name: 'EPL-2.0'},
        {compatibility: 0,name: 'MulanPSL-2.0'},
        {compatibility: 0,name: 'MulanPubL-2.0'},
        {compatibility: 0,name: 'Artistic-2.0'},
      ],
      cur_option: '',
      sort_options: [
        {
          label: "Sort By Popularity",
          value: 0
        },
        {
          label: "Sort By Readability",
          value: 1
        },
      ],
      file: '',
      loading: false,
      upload_disabled: false,
      git_disabled: false,
      git_address: {
        username: '',
        reponame: ''
      },
      check_res : {
        compatible_both_list: ['GPL-3.0-only'],
        compatible_combine_list: ['GPL-3.0-only', 'AGPL-3.0-only'],
        compatible_licenses: ['GPL-3.0-only', 'AGPL-3.0-only'],
        compatible_secondary_list: ['GPL-3.0-only'],
        confilct_copyleft_list: [],
        confilct_depend_dict: [{
          src_file: "MigrationHelperFrontend-master/MigrationHelperFrontend-master/LICENSE",
          src_license: 'AGPL-3.0-only',
          dest_file: "MigrationHelperFrontend-master/MigrationHelperFrontend-master/test1",
          dest_license: 'MIT'
        }],
        licenses_in_files: {
          "MigrationHelperFrontend-master/MigrationHelperFrontend-master/LICENSE": ["GPL-3.0-only", 'AGPL-3.0-only'],
          "MigrationHelperFrontend-master/MigrationHelperFrontend-master/test1": ['MIT'],
        }
      }
    }
  },
  mounted() {
    $('.file-url').hide()
    $('.description').show()
  },

  methods: {
    handleAvatarSuccess(res, file) {
      this.imageUrl = URL.createObjectURL(file.raw);
    },
    beforeAvatarUpload(file) {
      var len = file.name.length;
      var type = file.name.substr(len - 3, len)
      console.log(file.type);
      const isZIP = (type === 'rar' || type === 'zip');

      if (!isZIP) {
        this.$message.error('Only zip/rar files can be uploaded!');
      }

      return isZIP;
    },

    file_change(file, fileList) {
      this.file = file.raw;
      this.git_disabled = true;
    },

    remove_file() {
      this.git_disabled = false;
    },

    async upload_file_or_url() {
      var data;
      var url = ''
      var config = {
        headers: {
          "Content-Type": ''
        }
      }

      if (this.upload_disabled == false && this.git_disabled == true) {
        data = new FormData()
        data.append('file', this.file);
        url = '/api/zip'
        config.headers['Content-Type'] = 'multipart/form-data'
      } else if (this.upload_disabled == true && this.git_disabled == false) {
        data = {
          'username': this.git_address.username,
          'reponame': this.git_address.reponame,
        }
        console.log(data);
        url = '/api/git'
        config.headers['Content-Type'] = 'application/json';
      } else {
        this.$message.error('Please choose a file or input URL!')
        return
      }

      // res : {
      //   compatible_both_list: ['GPL-3.0-only'],
      //   compatible_combine_list: (2) ['GPL-3.0-only', 'AGPL-3.0-only'],
      //   compatible_licenses: (2) ['GPL-3.0-only', 'AGPL-3.0-only'],
      //   compatible_secondary_list: ['GPL-3.0-only'],
      //   confilct_copyleft_list: [],
      //   confilct_depend_dict: [],
      //   licenses_in_files: {}
      // }

      this.loading = true;
      this.axios.post(url, data, config)
      .then(res => {
        if (res.status == 200) {
          console.log(res.data);
          this.licenses = res.data.licenses_in_files;
          $('.file-url').hide()
          this.loading = false;
          $('.description').show()
        } else {
          console.log('wrong');
        }
      }).catch(res => {
        console.log(res);
        this.loading = false;
      })
    },

    enter_questions() {
      $("#uploader").hide()
      $("#description").hide()
      $("#questions").show()
      this.$router.push('/rec/questions')
    },

    git_change() {
      if (this.git_address.username == '' && this.git_address.reponame == '') {
        this.upload_disabled = false;
        $('.el-icon-upload').css('color', '#095da7')
      } else {
        this.upload_disabled = true;
        $('.el-icon-upload').css('color', 'black')
      }
    },

    show_confict_depend_dict() {
      for (const pair of this.check_res.confilct_depend_dict) {
        var src_lic = pair.src_license;
        var ele = "<b-popover target='"+src_lic+"' triggers='hover'>"+pair.dest_file+":"+pair.dest_license+"</b-popover>"
        console.log(ele);
        console.log(src_lic);
        // $('#description').append("<b-popover target='"+src_lic+"' triggers='click'>"+pair.dest_file+":"+pair.dest_license+"</b-popover>")
        $('#'+src_lic).append("<p>test</p>")
      }
    }
  }
}
</script>

<style>
.avatar-uploader .el-upload {
  /* margin-top: 50px; */
  border: 1px dashed #d9d9d9;
  border-radius: 10px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 35px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}

.circle {
  background: #456BD9;
  border: 10px solid #0F1C3F;
  border-radius: 50%;
  width: 15px;
}

.comp_type {
  background: #8c939d;
  border-radius: 50%;
  border: 20px solid black;
  width: 20px;
  height: 20px;

}

.el-step__title.is-process {
  color: rgb(21, 24, 26);
}

.main {
  position: relative;
  margin-top: 5%;
  left: 13%;
  width: 74%;
}

.steps {
  position: relative;
  top: 25px;
}

.el-card__header {
  background: #777;
}

.file-path {
  color: cornflowerblue
}
</style>