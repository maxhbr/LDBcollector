<template>
    <div id="app" v-loading="loading">
        <div id="main">
        <div class="header">开源许可证兼容性判断</div>
        <div id="choose">
            <!-- <b-form-select class="selector" v-model="selected_A" :options="options" label="许可证A"></b-form-select>
            <b-form-select class="selector" v-model="selected_B" :options="options" label="许可证B"></b-form-select> -->
            <el-row :gutter="2">
            <el-col :span="10" :offset="2">
                <el-select class="selector" v-model="selected_A" placeholder="许可证A">
                    <el-option v-for="item in options" key="item" :label="item" :value="item"></el-option>
                </el-select>
            </el-col>
            <el-col :span="10">
                <el-select class="selector" v-model="selected_B" placeholder="许可证B">
                    <el-option v-for="item in options" :key="item" :label="item" :value="item"></el-option>
                </el-select>
            </el-col>
            </el-row>
        </div>
        <div id="result" style="display: none">
            <el-divider></el-divider>
            <el-card style="height: 500px" class="card">
                <div>比较结果</div>
                <el-row>
                    <el-col :span="5"><span>兼容结果：</span></el-col>
                    <el-col :span="18"><div class="msg_left">{{result.iscompatibility}}</div></el-col>
                </el-row>
                <el-row>
                    <el-col :span="5"><span>如何使用：</span></el-col>
                    <el-col :span="18"><div class="msg_left">{{result.how_to_use}}</div><br style="clear:both"></el-col>
                    
                </el-row>
                <el-row>
                    <el-col :span="5"><span>原因分析：</span></el-col>
                    <el-col :span="18"><div class="msg_left">{{result.why_or_why_not}}</div></el-col>
                </el-row>
                <el-row>
                    <el-col :span="5"><span>影响次级兼容的条款：</span></el-col>
                    <el-col :span="18"><div class="msg_left">{{result.compatibility_terms}}</div></el-col>
                </el-row>
                
            </el-card>
        </div>
        <div><b-button @click="begin_query" variant="success" style="margin-top: 20px">开始比较</b-button></div>
        </div>
    </div>
</template>

<script>
import $ from 'jquery'
export default {
    name: 'query',
    data () {
        return {
            loading: false,
            selected_A: '',
            selected_B: '',
            options: [],
            result: {
                iscompatibility: '',
                how_to_use: '',
                why_or_why_not: '',
                compatibility_terms: []
            }
        }
    },
    mounted () {
        this.axios.post('/api/support_list')
        .then(res => {
            this.options = res.data;
            console.log(res.data);
        })
    },
    methods: {
        async begin_query() {
            var data = {
                'licenseA': this.selected_A,
                'licenseB': this.selected_B,
            }
            const config = {
                headers: {
                    "Content-Type": "application/json"
                }
            }
            this.axios.post('/api/query', data, config)
            .then(res => {
                this.result = res.data;
                if (this.result.why_or_why_not == '') {
                    this.result.why_or_why_not = '-'
                }
                if (this.result.compatibility_terms.length == 0) {
                    this.result.compatibility_terms = '-'
                }
            }).catch (res => {
                console.log('wrong');
            })


            $('#main').css({'height': '722px'})
            this.loading = true;
            $('.header').css('margin-top', '20px')
            $('#result').show();
            
            setTimeout(() => {
                this.loading = false;
            }, 500)
        }
    }
}
</script>

<style>
#main {
    height: 530px;
}

.header {
    position: relative;
    /* box-sizing: border-box; */
    width: 100%;
    height: 70px;
    font-size: 45px;
    /* box-shadow: 0 0 1px rgb(0 0 0 / 25%);
    transition: background-color 0.3s ease-in-out; */
    margin-top: 15%;
    color: #6a6a74;
}

.selector {
    width: 400px;
    height: 50px;
}

#choose {
    margin-top: 20px;
}

#result {
    margin-left: 15%;
    width: 70%;
    height: 500px;
}

.card {
    border-radius: 10%;
    box-shadow: 7px 6px 1px 1px #bbb2b2;
}

.el-row {
    min-height: 50px;
}

.msg_left {
		position: relative;
	    margin: 10px 10px;
	    max-width: 700px;
	    min-height: 20px;
	    padding: 8px;
	    /* border: solid 1px #6e6966; */
	    border-radius: 10px;
	    background: #d0e5e1;
	}
	.msg_left:before {
	    position: absolute;
	    top: 6px;
	    left: -20px;
	    padding: 0;
	    /* border: 10px solid; */
	    border-color: transparent #6e6966 transparent transparent;
	    display: block;
	    content: '';
	    z-index: 9;
	}
	.msg_left:after {
	    position: absolute;
	    top: 6px;
	    left: -18px;
	    padding: 0;
	    border: 10px solid;
	    border-color: transparent #d0e5e1 transparent transparent;
	    display: block;
	    content: '';
	    z-index: 10;
	}
</style>