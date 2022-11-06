<template>
  <div id="page">
    <!-- 步骤条 -->
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
                  <span style="color:white">License Compatibility Check</span>
                </div>
                <el-upload class="avatar-uploader" id="uploader" ref="uploader" action="#" :show-file-list="true"
                  :on-success="handleAvatarSuccess" :before-upload="beforeAvatarUpload" :on-change="file_change"
                  :limit=1 accept=".rar,.zip" drag :auto-upload="false" v-loading="loading">
                  
                  <i class="el-icon-upload" style="color: #095da7"></i>
                  <div class="el-upload__text">Drag the file here, or <em>click to upload</em></div>
                  <div class="el-upload__tip" slot="tip">Only zip/rar files can be uploaded</div>
                </el-upload>
                <div class="description" id="description" style="display: none">
                <span>The licenses in the project</span>
                <el-divider></el-divider>
                <div style="overflow-y:scroll; height: 350px;">
                <div v-for="(file, index) in licenses" style="text-align: left; margin: 10px">
                  <div>
                  <i class="el-icon-warning"></i><span style="color:cornflowerblue">{{index}}:</span>
                  <span v-for="license in file">
                    <span>{{license}},&nbsp</span>
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
                <span style="color:white">Recommendation List</span>
              </div>
              <div class="dropdown">
                <!-- <el-dropdown trigger="click">
                <span class="el-dropdown-link">
                  排序方式<i class="el-icon-arrow-down el-icon--right"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                <el-dropdown-item icon="el-icon-plus">按流行度降序</el-dropdown-item>
                <el-dropdown-item icon="el-icon-circle-plus">按流行度升序</el-dropdown-item>
                </el-dropdown-menu>
                </el-dropdown> -->
                <el-select v-model="cur_option" placeholder="请选择">
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
                <el-table-column label="兼容性" width="70" >
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
          <b-button type="primary" @click="upload_file">Start check</b-button>
          <b-button type="primary" @click="enter_questions" style="display: none">Next step</b-button>
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
          label: "按流行度排序",
          value: 0
        },
        {
          label: "按可读性排序",
          value: 1
        },
      ],
      file: '',
      loading: false
    }
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
        this.$message.error('上传文件只能是zip和rar格式!');
      }

      return isZIP;
    },

    file_change(file, fileList) {
      this.file = file.raw;
    },

    async upload_file() {
      var fd = new FormData();
      fd.append('file', this.file);
      const config = {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      }
      this.loading = true;
      this.axios.post('/api/zip', fd, config)
      .then(res => {
        if (res.status == 200) {
          console.log(res.data);
          this.licenses = res.data.licenses_in_files;
          var uploader = document.getElementById("uploader")
          uploader.setAttribute("style", "display: none")
          this.loading = false;
          var description = document.getElementById("description")
          description.setAttribute("style", "display: content")
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
    }
  }
}
</script>

<style>
.avatar-uploader .el-upload {
  margin-top: 50px;
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
</style>