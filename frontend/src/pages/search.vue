/*
检测页面
包含上传文件、兼容性检测和推荐功能
*/
<template>
  <div id="page">
    <!-- 步骤条 -->
    <div class="steps">
      <el-steps :active="step_active" align-center finish-status="success">
        <el-step title="兼容性检测"></el-step>
        <el-step title="条款偏好选择"></el-step>
        <el-step title="要素对比"></el-step>
      </el-steps>
    </div>

    <div id="main" class="main">
      <el-row :gutter="20" style="margin-top: 20px; height: 500px">
        <el-col :span="18">
          <div class="file_box">
            <div>
              <el-card style="height: 500px;">
                <div slot="header" class="clearfix">
                  <span>开源许可证兼容性检测</span>
                </div>
                <el-upload class="avatar-uploader" id="uploader" ref="uploader" action="#" :show-file-list="true"
                  :on-success="handleAvatarSuccess" :before-upload="beforeAvatarUpload" :on-change="file_change"
                  :limit=1 accept=".rar,.zip" drag :auto-upload="false" v-loading="loading">
                  
                  <i class="el-icon-upload" style="color: #095da7"></i>
                  <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                  <div class="el-upload__tip" slot="tip">只能上传zip/rar文件</div>
                </el-upload>
                <div class="description" id="description" style="display: none">
                <span>项目中已有的开源许可证</span>
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
        <el-col :span="6">
          <div class="list">
            <el-card style="height: 500px">
              <div slot="header" class="clearfix">
                <span>开源许可证推荐列表</span>
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
              <el-table :data="table_data">
                <el-table-column label="兼容性" width="70">
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
          <el-button type="primary" @click="upload_file">上传</el-button>
          <el-button type="primary" @click="enter_questions" style="display: none">问题</el-button>
        </el-col>
        <el-col :span="6">

        </el-col>
      </el-row>
      <el-row>
        <el-col :span="24">
          <div style="margin-top: 20px; background: azure; height: 100px">开源许可证说明</div>
        </el-col>
      </el-row>
    </div>
  </div>

</template>

<script>
import $ from 'jquery'
export default {
  name: 'search',
  data() {
    return {
      step_active: 0,
      licenses: [["MIT"], [ "GPL-2.0-only", "LGPL-2.1-or-later", "BSL-1.0", "Apache-2.0", "GPL-2.0-or-later"], ["LicenseRef-scancode-wordnet", "LicenseRef-scancode-public-domain", "LicenseRef-scancode-other-permissive", "LicenseRef-scancode-mit-old-style"]],
      table_data: [
        {
          compatibility: 0,
          name: '许可证1'
        },
        {
          compatibility: 0,
          name: '许可证1'
        },
        {
          compatibility: 0,
          name: '许可证1'
        },
        {
          compatibility: 0,
          name: '许可证1'
        },

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
          this.licenses = res.data;
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
      this.$router.push('/search/questions')
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
  border: 15px solid #0F1C3F;
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
  color: aliceblue;
}

.main {
  position: relative;
  margin-top: 5%;
  left: 17%;
  width: 66%;
}

.steps {
  position: relative;
  top: 25px;
}

.el-card__header {
  background: azure;
}
</style>