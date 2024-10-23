<template>

    <div id="page" class="wrapper">


        <div class="introduce">
            <!-- <img class="logo" src="../assets/icon.png"> -->
            <div class="text">
                <el-card shadow="always" class="card">
                    <div>
                        <b-img :src="require('../assets/logo.png')" rounded="circle" alt="Circle image" width="140px">
                        </b-img>
                        <div>
                            
                            <b-jumbotron>
                                <template #header>LicenseRec</template>

                                <template #lead >

                                   <p style="width:600px;margin-left:auto;margin-right: auto;justify;text-align-last: center;font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;">Note! The opinions provided by this tool are for reference only and do not represent the opinions of lawyers, please consult a lawyer if necessary!</p>

                                </template>

                                <hr class="my-4">
                                <p style='font-family:Comic Sans MS, Comic Sans, cursive'>
                                    The source code of this tool is available at <b-link href="https://github.com/osslab-pku/RecLicense" target="_blank">Github</b-link>, and the demonstrated video is on <b-link href="https://video.licenserec.com" target="_blank">Youtube</b-link>.
                                </p>
                                <hr class="my-4">
                                <p style='font-family:Comic Sans MS, Comic Sans, cursive'>
                                    If you have any questions, you can contact Weiwei Xu, email: xuww At stu.pku.edu.cn.
                                </p>
                                <hr class="my-4">

                            </b-jumbotron>
                        </div>
                    </div>
                </el-card>
            </div>
            <p></p>
        </div>

        <!-- <keep-alive>
            <router-view id='img' ref="child" />
        </keep-alive> -->
    </div>
</template>

<script>
export default {
    components: {
    },
    name: 'about',
    data() {
        return {
        }
    },
    mounted() {

    },
    methods: {
    }
}
</script>

<style scoped>
#bg-particles {
    position: absolute;
    width: 100%;
    height: 100%;
    background-position: 50% 50%;
    background-repeat: no-repeat;
    background-size: cover;
}

#page {
    height: 100%
}

#word-text-area {
    margin-left: 20%;
    margin-right: 20%;
}

#img {
    margin-left: 10px;
    margin-right: 10px;
    margin-top: 30px;
    width: 100%;
    height: 700px
}

.wrapper {
    width: 100%;
    height: 100%;
    /* background: #f0f0f0; */
}

.header {
    position: relative;
    box-sizing: border-box;
    width: 100%;
    height: 70px;
    font-size: 22px;
    box-shadow: 0 0 1px rgb(0 0 0 / 25%);
    transition: background-color 0.3s ease-in-out;
}

.header {
    position: relative;
    box-sizing: border-box;
    width: 100%;
    height: 70px;
    font-size: 22px;
    box-shadow: 0 0 1px rgb(0 0 0 / 25%);
    transition: background-color 0.3s ease-in-out;
}

.logo {
    float: left;
    margin-left: 60px;
    height: 70px;
    width: 160px;
    font-size: 25px;

    border: 0
}

.introduce {
    margin-top: 150px;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 100px;

}

.card {
    /* background: rgb(154, 156, 156); */
    margin-left: auto;
    margin-right: auto;
    width: 800px;
    height: 550px;

}

/* .text {
    margin-left: 20%;
    width: 60%;
} */
</style>