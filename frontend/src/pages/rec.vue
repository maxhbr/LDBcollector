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
      <el-row :gutter="20" style="margin-top: 20px; height: 600px">
        <el-col :span="17">
          <div class="file_box">
            <div>
              <el-card style="height: 600px;">
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
                <div style="overflow-y:scroll; height: 450px;">
                <!-- <b-popover target="AGPL-3.0-only" triggers="hover" disabled="true"><span style="color:cornflowerblue">MigrationHelperFrontend-master/MigrationHelperFrontend-master/test1</span><span>:MIT</span></b-popover> -->

                  <!-- <div v-for="(licenses, file) in check_res.licenses_in_files" style="text-align: left; margin: 10px">
                    <div>
                    <i class="el-icon-warning"></i><span class="file-path">{{file}}:</span>
                    <span v-for="license, index in licenses">
                      <span :id="license">{{license}},&nbsp</span>
                    </span>
                    </div>
                  </div> -->

                  <el-table :data="licenses_in_files_list" :span-method="span_method" :row-class-name="licenses_row_class">
                    <el-table-column width="50px">
                      <template slot-scope="scope"><i class="el-icon-warning"></i></template>
                      <!-- <el-table-column prop="path"></el-table-column> -->
                    </el-table-column>
                    <el-table-column prop="path" label="path"></el-table-column>
                    <el-table-column label="license">
                      <template slot-scope="scope"><span>{{scope.row.license}}</span></template>
                    </el-table-column>
                  </el-table>

                </div>
                </div>
                <div>
                <div id="questions">
                  <questions @question_over="change_rec_license"></questions>
                </div>
                </div>
              </el-card>
            </div>
          </div>
        </el-col>
        <el-col :span="7">
          <div class="list">
            <el-card style="height: 600px">
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
              <el-table :data="table_data" style="overflow-y: scroll; height: 460px" :row-class-name="tabel_row_class">
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
          <b-button id="upload-button" variant="success" @click="upload_file_or_url">Start check</b-button>
          <b-button id="question-button"  @click="enter_questions">Next step</b-button>
          <b-button id="skip-button"  @click="enter_questions">Skip this step</b-button>
          <b-button id="back-button"  @click="back_upload" style="display: none">Previous Step</b-button>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span="24">
          <div style="margin-top: 20px; background: azure; height: 100px; text-align: left;">
            <div v-for="conflict in check_res.confilct_copyleft_list" >
            <i class="el-icon-warning"></i>
            <span>{{conflict}}</span>
            </div>
          </div>
        </el-col>
      </el-row>
      
    </div>
  </div>

</template>

<script>
import $ from 'jquery'
import questions from '../components/questions.vue'
export default {
  name: 'rec',
  components: {questions},
  data() {
    return {
      licenses_in_files_list: [],
      span_arr: [],
      support_list: [],
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
        compatible_both_list: [],
        compatible_combine_list: [],
        compatible_licenses: [],
        compatible_secondary_list: [],
        confilct_copyleft_list: [],
        confilct_depend_dict: [],
        licenses_in_files: {}
      }
    }
  },
  mounted() {
    $('.file-url').show()
    $('#questions').hide()
    $('#questions-button').hide()
    $('.description').hide()
    this.axios.post('/api/support_list')
    .then(res => {
      this.support_list = res.data;
    })
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

    // 答题完成后，更改推荐列表
    change_rec_license(val) {
      for (const [license, index] of this.table_data.entries()) {
        if (!this.has(val, license.name)) {
          this.table_data.splice(index, 1)
        }
      }
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

      this.loading = true;
      this.axios.post(url, data, config)
      .then(res => {
        if (res.status == 200) {
          console.log(res.data);
          this.check_res = res.data;
          this.table_data = [];
          for (const license of res.data.compatible_licenses) {
            this.table_data.push({name: license})
          }
          this.generate_licenses_list();
          $('.file-url').hide()
          this.loading = false;
          $('#description').show()
          $('#upload-button').hide()
          $('#question-button').show()
        } else {
          console.log('wrong');
        }
      }).catch(res => {
        console.log(res);
        this.loading = false;
      })
    },

    // 进入答题界面
    enter_questions() {
      $(".file-url").hide()
      $("#description").hide()
      $("#back-button").show()
      $("#skip-button").hide()
      $("#upload-button").hide()
      $("#questions").show()
      this.step_active = 1
    },

    back_upload() {
      $(".file-url").show()
      $("#description").hide()
      $("#back-button").hide()
      $("#skip-button").show()
      $("#upload-button").show()
      $("#questions").hide()
      this.step_active = 0
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
        $('.'+src_lic).append("<p>test</p>")
        $('.'+src_lic).attr('disabled', 'false')
        // $('#description').append("<b-popover target='"+src_lic+"' triggers='click'>"+pair.dest_file+":"+pair.dest_license+"</b-popover>")
        // $('#description').append("<p>test</p>")
      }
      // $('#description').append("<p>test</p>")

    },

    generate_licenses_list() {
      this.licenses_in_files_list = [];
      this.span_arr = [];
      for (const path in this.check_res.licenses_in_files) {
        for (const license of this.check_res.licenses_in_files[path]) {
          this.licenses_in_files_list.push({'path': path, 'license': license})
        }
      }
      console.log(this.licenses_in_files_list);

      var contactDot = 0;
      this.licenses_in_files_list.forEach( (item,index) => {
      //遍历tableData数据，给span_arr存入一个1，第二个item.path和前一个item.path是否相同，相同就给
      //span_arr前一位加1，span_arr再存入0，因为span_arr为n的项表示n项合并，为0的项表示该项不显示,后面有span_arr打印结果
      if(index===0){
        this.span_arr.push(1)
      }else{
        if(item.path === this.licenses_in_files_list[index-1].path){
          this.span_arr[contactDot] += 1;
          this.span_arr.push(0)
        }else{
          contactDot = index
          this.span_arr.push(1)
          }
        }
      })
      console.log(this.span_arr);
    },

    span_method({row, column, rowIndex, columnIndex}) {
      if (columnIndex === 1) {
        var _row = this.span_arr[rowIndex];
        var _col = _row > 0 ? 1 : 0;
        return {
          rowspan: _row,
          colspan: _col,
        }
        }
    },

    licenses_row_class({row, rowIndex}) {
      console.log(row);
      for (const pair of this.check_res.confilct_depend_dict) {
        if (row.license == pair.dest_license || row.license == pair.src_license) {
          return "conflict-license";
        }
      } 
      for (const support of this.support_list) {
        if (row.license == support) {
          return "support-license";
        }
      }
    },

    show_compatible_list() {

    },


    has(arr, name) {
      var res = arr.find(item => item == name);
      if (res) {
        return true;
      }
      return false;
    },

    tabel_row_class({row, rowIndex}) {
      if (this.has(this.check_res.compatible_both_list, row.name)) {
        return "both-row"
      }
      if (this.has(this.check_res.compatible_secondary_list, row.name)) {
        return "secondary-row"
      }
      if (this.has(this.check_res.compatible_combine_list, row.name)) {
        return "combine-row"
      }
    }
  }
}
</script>

<style>
.both-row > * > * >.circle {
  border: 10px solid #1230da;
}

.secondary-row > * > * >.circle {
  border: 10px solid #28d811;
}

.combine-row > * > * >.circle {
  border: 10px solid #c7db11;
}

.conflict-license > * > * > i::before {
  content: "\e79d"
}

.conflict-license > * >  .cell > span{
  color: red
}

.support-license  > * > * > i::before {
  content: "\e79c"
}

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
  margin-left: 10px
}

.circle.both {
  background: #0F1C3F;
}

.circle.combine {
  background: #c7db11;
}

.circle.secondary {
  background: #0cb1a8;
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

.el-card__body {
  height: 540px;
}

.file-path {
  color: cornflowerblue
}
</style>