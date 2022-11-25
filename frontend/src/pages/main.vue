<template>

    <div id="page" class="wrapper">

        <!-- <div class="header">
            <button class="logo" @click="logo"></button>
             <img class="logo" src="../assets/icon.png"> 
        </div> -->


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

                                <template #lead>

                                    Are you confused when choosing an open source license for your project? <br />
                                    Try our tool!

                                </template>

                                <hr class="my-4">
                                <p style='font-family:Comic Sans MS, Comic Sans, cursive'>
                                    Our tool provides the function of open source license recommendation and <br />open 
                                    source license compatibility query. It trys to recommend the most suitable <br /> 
                                    open source license for you in a personalized way!
                                </p>
                                <hr class="my-4">
                                <b-button to="/rec">Choose a License</b-button>
                                <b-button @click="jump_query">Compatibility query</b-button>
                                <b-button to="/guide">Guideline</b-button>
                                <b-button style="height:38px" href="https://github.com/osslab-pku/RecLicense"
                                    target="_blank">
                                    <b-img style="height:24px" :src="require('../assets/github.svg')" fluid></b-img>
                                    
                                </b-button>
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
    name: 'main',
    data() {
        return {
            text: '',
            pic: "",
            loading: false,
            activeIndex: 1,
        }
    },
    mounted() {

    },
    methods: {
        handleSelect(key, keyPath) {
            console.log(key, keyPath);
        },

        jump_rec() {
            this.$router.push('/rec');
        },

        jump_query() {
            this.$router.push('/query');
        },
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