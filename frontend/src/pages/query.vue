<template>
    <div id="app" v-loading="loading">
        <div id="main">
            <div>
                <b-card class="query_card">
                    <b-jumbotron>
                        <template v-slot:header>Open Source License Compatibility Query</template>

                        <template v-slot:lead>
                            Please select two license to query their compatibility.
                        </template>

                        <hr class="my-4">

                        <p style='font-family:Comic Sans MS, Comic Sans, cursive'>
                            NOTE! License compatibility is directional. License A is compatible with License B <br />if
                            the software
                            licensed under License A is modified or combined with other software <br />and the
                            resulting derivative software as a whole can be licensed under License B.
                        </p>

                        <el-select class="selector" v-model="selected_A" placeholder="LicenseA">
                            <el-option v-for="item in options" :key="item" :label="item" :value="item"></el-option>
                        </el-select>
                        <el-select class="selector" v-model="selected_B" placeholder="LicenseB">
                            <el-option v-for="item in options" :key="item" :label="item" :value="item"></el-option>
                        </el-select>
                        <hr class="my-4">

                        <div id="result" style="display: none">
                            <el-row>
                                <el-col :span="6" class="label"><span>兼容结果：</span></el-col>
                                <el-col :span="18">
                                    <div class="msg_left">{{ result.iscompatibility }}</div>
                                </el-col>
                            </el-row>
                            <el-row>
                                <el-col :span="6" class="label"><span>如何使用：</span></el-col>
                                <el-col :span="18">
                                    <div class="msg_left">{{ result.how_to_use }}</div><br style="clear:both">
                                </el-col>

                            </el-row>
                            <el-row>
                                <el-col :span="6" class="label"><span>原因分析：</span></el-col>
                                <el-col :span="18">
                                    <div class="msg_left">{{ result.why_or_why_not }}</div>
                                </el-col>
                            </el-row>
                            <el-row>
                                <el-col :span="6" class="label"><span>影响次级兼容的条款：</span></el-col>
                                <el-col :span="18">
                                    <div class="msg_left" v-for="term in result.compatibility_terms">{{ term }}</div>
                                </el-col>
                            </el-row>


                        </div>
                        <div>
                            <b-button @click="begin_query" style="margin-top:20px">Query</b-button>
                        </div>
                    </b-jumbotron>

                </b-card>
            </div>


        </div>
    </div>
</template>

<script>
import $ from 'jquery'
export default {
    name: 'query',
    data() {
        return {
            loading: false,
            selected_A: '',
            selected_B: '',
            options: [],
            result: {
                iscompatibility: '-',
                how_to_use: '-',
                why_or_why_not: '-',
                compatibility_terms: []
            }
        }
    },
    mounted() {
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
                        this.result.compatibility_terms = ['-']
                    }
                }).catch(res => {
                    console.log('wrong');
                })

            var card_height = $('.card-body').css('height').substr(0, 3)
            console.log(card_height);
            var new_height = parseInt(card_height) + 100
            console.log(new_height);
            $('#main').css({ 'height': String(new_height+430)+'px' })
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
    height: 630px;
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
    /* height: 500px; */
}

.query_card {
    /* border-radius: 10%;
    box-shadow: 7px 6px 1px 1px #bbb2b2; */
    width: 80%;
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;

}

.label {
    margin-top: 15px;
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