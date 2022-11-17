<template>
  <div id="page" >
    <div class="steps">
      <el-steps :active="step_active" align-center finish-status="success">
        <el-step title="Compatibility Check"></el-step>
        <el-step title="Preferences"></el-step>
        <el-step title="Term Comparison"></el-step>
      </el-steps>
    </div>

    <div id="main1" class="main1" style="height: auto">
      <el-row :gutter="20" style="margin-top: 20px; height: 600px">
        <el-col :span="16">
          <div class="file_box">
            <div>
              <el-card style="height: 600px;">
                <div slot="header" class="clearfix">
                  <span style="font-size: 20px;color:white">License Compatibility Check</span>
                </div>
                <div class="file-url" v-loading="loading" element-loading-text="It may take a while...">
                <p style="font-size: 17px; font-weight:400;">You can upload your project or input Github repository url. If you want to choose a license for a new project, you can just <b style="color:red">skip this step</b>.</p>
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
                  <el-table :data="licenses_in_files_list" :span-method="span_method" :row-class-name="licenses_row_class" empty-text="No data">
                    <el-table-column width="50px">
                      <template slot-scope="scope"><i class="el-icon-warning"></i></template>
                    </el-table-column>
                    <el-table-column prop="path" label="path"></el-table-column>
                    <el-table-column label="license">
                      <template slot-scope="scope">
                        <el-popover placement="bottom" width="400" trigger="hover">
                          <span>{{depend_dict[scope.row.license]}}</span>
                          <span slot="reference">{{scope.row.license}}</span>

                        </el-popover>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                </div>

                <div>
                <div id="questions">
                  <questions @question_over="change_rec_license"></questions>
                </div>
                <div id="compare">
                  <compare :licenses="table_data" ref="compare_comp"></compare>
                </div>
                </div>
              </el-card>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="list">
            <el-card style="height: 600px">
              <div slot="header" class="clearfix">
                <span style="font-size: 20px;color:white">Recommendation List</span>
              </div>
              <div class="dropdown">
                <el-select v-model="cur_option" placeholder="Please choose" @change="sort_license($event)">
                  <el-option v-for="item in sort_options" :key="item.value" :label="item.label" :value="item.value">
                  </el-option>
                </el-select>
              </div>

              <!-- Reconmmend List -->
              <el-table :data="table_data" style="overflow-y: scroll; height: 460px;" :row-class-name="tabel_row_class" empty-text="No data">
                <el-table-column label="Compatibility" width="110" align="center">
                  <template slot-scope="scope">
                    <div class="circle"></div>
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="Name" width="200"></el-table-column>
              </el-table>

            </el-card>
          </div>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span="24">
          <div style="margin-top: 20px; text-align: left; ">
            <div id="question-icons">
              <i class="el-icon-error" ></i><span>: There is a compatibility conflict between the licenses of files that have a dependent relationship.</span>
              <i class="el-icon-success" ></i><span>: There is no conflict as described above. </span>
              <i class="el-icon-warning" ></i><span>: Do not support checking the compatibility of this license, please check manually.</span>
              <i class="circle" style="border-color: #1230da"></i><span>: Both secondarily compatible and combinatively compatible.</span>
              <i class="circle" style="border-color: #28d811"></i><span>: Secondarily compatible.</span>
              <i class="circle" style="border-color: #c7db11"></i><span>: Combinatively compatible.</span>
            </div>
            <div id="term-icons">
              <span class="icon-success"><i class="temp"></i></span><span>&nbsp&nbsp:The clause is explicitly included.</span>
              <span class="icon-wrong"><i class="temp"></i></span><span>&nbsp&nbsp:The clause is not mentioned.</span>
              <i class="circle" style="border-color: #1230da"></i><span>:Both secondarily compatible and combinatively compatible.</span>
              <i class="circle" style="border-color: #28d811"></i><span>:Secondarily compatible.</span>
              <i class="circle" style="border-color: #c7db11"></i><span>:Combinatively compatible.&nbsp</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="18">

          <span id="upload-span"><b-button id="upload-button" variant="success" @click="upload_file_or_url">Start checking</b-button></span>
          <span id="back-span"><b-button id="back-button"  @click="back_upload">Previous Step</b-button></span>
          <span id="question-span"><b-button id="question-button"  @click="enter_questions(false)">Next step</b-button></span>
          <span id="skip-span"><b-button id="skip-button"  @click="skip_upload">Skip this step</b-button></span>
          <span id="reupload-span"><b-button variant="success" @click="reupload">Reupload</b-button></span>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span="24">
          <div style="margin-top: 20px; background: azure; text-align: left;" id="copyleft-area">
            <p>Copyleft compatibility conflict:</p>
            <div v-for="conflict in check_res.confilct_copyleft_list" >
            <i class="el-icon-error" style="color: red"></i>
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
import compare from '../components/compare.vue'
export default {
  name: 'rec',
  components: {questions, compare},
  data() {
    return {
      depend_dict: {},
      licenses_in_files_list: [],
      span_arr: [],
      support_list: [],
      step_active: 0,
      // licenses: [["MIT"], [ "GPL-2.0-only", "LGPL-2.1-or-later", "BSL-1.0", "Apache-2.0", "GPL-2.0-or-later"], ["LicenseRef-scancode-wordnet", "LicenseRef-scancode-public-domain", "LicenseRef-scancode-other-permissive", "LicenseRef-scancode-mit-old-style"]],
      table_data: [
        {compatibility: 0,name: 'MIT', readability: 59.57333333, usage: 59986},
        {compatibility: 0,name: 'Apache-2.0', readability: 481.73, usage: 14537},
        {compatibility: 0,name: 'GPL-3.0-only', readability: 1699.506667, usage: 9039},
        {compatibility: 0,name: 'BSD-3-Clause', readability: 75.61666667, usage: 2503},
        {compatibility: 0,name: 'GPL-2.0-only', readability: 894.4466667, usage: 1958},
        {compatibility: 0,name: 'AGPL-3.0-only', readability: 1666.586667, usage: 1678},
        {compatibility: 0,name: 'MPL-2.0', readability: 710.0233333, usage: 1027},
        {compatibility: 0,name: 'LGPL-3.0-only', readability: 375.79, usage: 912},
        {compatibility: 0,name: 'BSD-2-Clause', readability: 66.61, usage: 884},
        {compatibility: 0,name: 'Unlicense', readability: 66.02333333, usage: 777},
        {compatibility: 0,name: 'ISC', readability: 42.13666667, usage: 623},
        {compatibility: 0,name: 'EPL-1.0', readability: 516.8866667, usage: 421},
        {compatibility: 0,name: 'CC0-1.0', readability: 327.7833333, usage: 376},
        {compatibility: 0,name: 'LGPL-2.1-only', readability: 1315.186667, usage: 310},
        {compatibility: 0,name: 'WTFPL', readability: 28.14333333, usage: 184},
        {compatibility: 0,name: 'Zlib', readability: 48.56, usage: 139},
        {compatibility: 0,name: 'EPL-2.0', readability: 646.26, usage: 138},
        {compatibility: 0,name: 'MulanPSL-2.0', readability: 235.5233333, usage: 0},
        {compatibility: 0,name: 'MulanPubL-2.0', readability: 409.6733333, usage: 0},
        {compatibility: 0,name: 'Artistic-2.0', readability: 417.62, usage: 43},
      ],
      static_table: [],
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
        confilct_depend_dict: [{
          src_file: '',
          src_license: '',
          dest_file: '',
          dest_license: ''
        }],
        licenses_in_files: {}
      }
    }
  },

  mounted() {
    $('.file-url').show()
    $('#questions').hide()
    $('#question-span').hide()
    $('#reupload-span').hide()
    $('#back-span').hide()
    $('.description').hide()
    $("#term-icons").hide()
    $("#compare").hide()
    $("#copyleft-area").hide()
    this.static_table = this.table_data;
    this.axios.post('/api/support_list')
    .then(res => {
      this.support_list = res.data;
    })

    // this.timer = window.setInterval(() => {
    //   setTimeout(() => {
    //     this.test()
    //   }, 0)
    // }, 2000);
  },

  destroyed() {
    // window.clearInterval(this.timer);
  },

  methods: {
    // test() {
    //   var data = {testdata: 'test'}
    //   const config = {
    //     headers: {
    //       "Content-Type": "application/json"
    //     }
    //   }
    //   this.axios.post('/api/test', data, config)
    //   .then(res => {
    //     console.log(res);
    //   }).catch(res => {
    //     console.log(res);
    //   }) 
    // },


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

    // 答题完成后，更改推荐列表并显示要素对比
    change_rec_license(val) {
      var temp_table = []
      for (const license of this.table_data) {
        if (this.has(val, license.name)) {
          temp_table.push(license)
        }
      }
      this.table_data = temp_table;
      this.$refs.compare_comp.term_compare(this.table_data);

      this.step_active = 2;
      $('#compare').show();
      $('#questions').hide();
      $("#back-span").hide()
      $("#reupload-span").show()
      $("#question-icons").hide()
      $("#term-icons").show()

      if (this.table_data.length == 0) {
        this.$message.error("There are no recommended licenses according to your preference!")
      } else {
        this.$message.success("A list of recommended licenses has been produced based on your preferences!")
        this.step_active = 3;
      }
    },

    // 对推荐列表进行排序
    sort_license(val) {
      // 流行度
      // console.log(val);
      if (val == 0) {
        this.table_data.sort((first, second) => {
          return second.usage - first.usage;
        })
      }
      // 可读性
      if (val == 1) {
        this.table_data.sort((first, second) => {
          return second.readability - first.readability;
        })
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
          console.log(res);
          if (res.data != "URL ERROR") {
            config.headers['Content-Type'] = 'application/json';
            var unzip_path = res.data;
            console.log(unzip_path);
            var timer = window.setInterval(() => {
              console.log("tick");
              this.axios.post('/api/poll', {path: unzip_path}, config)
              .then(res => {
                if (res.data != 'doing') {
                  console.log(res.data);
                  this.check_res = res.data;
                  window.clearInterval(timer)
                  this.upload_done()
                }
              })
            }, 2000)
            // this.check_res = res.data;
            // this.table_data = [];
            // for (const license of res.data.compatible_licenses) {
            //   this.table_data.push({name: license})
            // }
            // var temp_table = []
            // for (const license of this.table_data) {
            //   if (this.has(res.data.compatible_licenses, license.name)) {
            //     temp_table.push(license)
            //   }
            // }
            // this.table_data = temp_table;
            // this.generate_licenses_list();
            // this.generate_depend_dict();
            // $('.file-url').hide()
            // $('#description').show()
            // $('#upload-span').hide()
            // $('#skip-span').hide()
            // $('#question-span').show()
            // $("#back-span").show()
            // $("#copyleft-area").show()
          } else if (res.data == "URL ERROR") { // git url is wrong
            this.$message.error("Make sure the git url is correct!")
          }
          // this.loading = false;
          
        } else {
          console.log('upload_file_or_url wrong');
        }
      }).catch(res => {
        console.log(res);
        // this.loading = false;
      })
    },

    upload_done() {
        var temp_table = []
          for (const license of this.table_data) {
            if (this.has(this.check_res.compatible_licenses, license.name)) {
              temp_table.push(license)
            }
          }
          this.table_data = temp_table;
          this.generate_licenses_list();
          this.generate_depend_dict();
          $('.file-url').hide()
          $('#description').show()
          $('#upload-span').hide()
          $('#skip-span').hide()
          $('#question-span').show()
          $("#back-span").show()
          $("#copyleft-area").show()
          this.loading = false;
    },

    // 进入答题界面
    enter_questions(is_skip) {
      if (is_skip || this.check_res.confilct_copyleft_list.length == 0) {
        console.log('enter');
        $(".file-url").hide()
        $("#description").hide()
        $("#skip-span").hide()
        console.log('tag1');
        $("#upload-span").hide()
        $("#question-span").hide()
        $("#questions").show()
        $("#back-span").show()

        this.step_active = 1
      } else {
        this.$message.error("Make sure there are no conflicts in files until you proceed to next step!")
      }
      
      // console.log('enter');
      // $(".file-url").hide()
      // $("#description").hide()
      // $("#skip-span").hide()
      // console.log('tag1');
      // $("#upload-span").hide()
      // $("#question-span").hide()
      // $("#questions").show()
      // $("#back-span").show()

      // this.step_active = 1
    },

    skip_upload() {
      console.log('skip');
      this.check_res.compatible_both_list = ['MIT', 'Apache-2.0','GPL-3.0-only','BSD-3-Clause','GPL-2.0-only', 'AGPL-3.0-only', 'MPL-2.0','LGPL-3.0-only','BSD-2-Clause','Unlicense','ISC','EPL-1.0','CC0-1.0','LGPL-2.1-only','WTFPL','Zlib','EPL-2.0','MulanPSL-2.0','MulanPubL-2.0','Artistic-2.0'];
      this.enter_questions(true);
    },

    back_upload() {
      console.log('back');
      $(".file-url").show()
      $("#description").hide()
      $("#back-span").hide()
      $("#skip-span").show()
      $("#question-span").hide()
      $("#upload-span").show()
      $("#questions").hide()
      $("#copyleft-area").hide()
      this.table_data = this.static_table;
      // this.check_res = {}
      this.check_res.confilct_copyleft_list = [],
      this.check_res.compatible_both_list = [],
      this.step_active = 0
    },

    reupload() {
      this.$router.go(0)
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

    generate_licenses_list() {
      this.licenses_in_files_list = [];
      this.span_arr = [];
      for (const path in this.check_res.licenses_in_files) {
        for (const license of this.check_res.licenses_in_files[path]) {
          this.licenses_in_files_list.push({'path': path, 'license': license})
        }
      }

      var contactDot = 0;
      this.licenses_in_files_list.forEach( (item,index) => {
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
    },

    generate_depend_dict() {
      var temp_depend = {};
      for (const license_in_file of Object.values(this.check_res.licenses_in_files)) {
        for (const license of license_in_file) {
          temp_depend[license] = ''
        }
      }
      console.log(temp_depend);
      for (const license of this.check_res.confilct_depend_dict) {
        temp_depend[license.src_license] += 'Incompatibile with ' + license.dest_file + ':' + license.dest_license + ';'
        temp_depend[license.dest_license] += 'Incompatibile with ' + license.src_file + ':' + license.src_license + ';'
      }
      console.log(temp_depend);
      this.depend_dict = temp_depend;
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
    },


  }
}
</script>

<style>
.both-row > * > * >.circle {
  border: 7px solid #1230da;
}

.secondary-row > * > * >.circle {
  border: 7px solid #28d811;
}

.combine-row > * > * >.circle {
  border: 7px solid #c7db11;
}

.conflict-license > * > * > i::before {
  content: "\e79d";
  color: red;
}

.conflict-license > * >  .cell > span{
  color: red
}

.support-license  > * > * > i::before {
  content: "\e79c";
  color: #28d811;
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
  border: 7px solid #0F1C3F;
  border-radius: 50%;
  /* width: 15px; */
  /* margin-left: 10px; */
  /* font-family: element-icons!important; */
    font-style: normal;
    font-weight: 400;
    font-variant: normal;
    text-transform: none;
    line-height: 1;
    vertical-align: baseline;
    display: inline-block;
    -webkit-font-smoothing: antialiased;
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

.main1 {
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

.el-icon-success {
  color: #28d811;
}

.el-icon-error {
  color: red;
}

.temp {
    text-align: center;
}

.icon-success > .temp, .icon-wrong > .temp {
    position: relative;
    /* font-size: 1; */
    height: 20px;
    width: auto;
    margin-left: 15px;
}

.icon-success > .temp::before{
    content: '√';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    line-height: 16px;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    color: rgb(22, 194, 74);
    border: 2px solid rgb(22, 194, 74);
    border-radius: 50%;
}

.icon-wrong > .temp::before{
    content: '×';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    line-height: 16px;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    color: red;
    border: 2px solid red;
    border-radius: 50%;
}
</style>