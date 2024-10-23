<template>
    <div>
        <div>
            <el-card style="width: 1400px; position: relative; display: inline-block; margin-top: 50px;">
                <div slot="header">
                    <span style="font-size: 40px; font-weight: bold">Classification and characteristics of business models</span><br>
                    <span style='font-family:Comic Sans MS, Comic Sans, cursive; text-align: left;'>The essence of open source business model is how open source enterprises can create value for 
                        customers while extracting some benefits for themselves. Common open source business models and 
                        their licensing features mainly include the following:</span>
                </div>

                <el-row>
                    <el-col :span="10">
                        <!-- <el-image src="../assets/opensource2.jpeg" style="height: 500px; width: 400px; display: inline-block"></el-image> -->
                        <img src="../assets/opensource2.jpeg" style="height: 500px; width: 100%; display: inline-block"/>
                    </el-col>
                    <el-col :span="14">
                    <el-carousel trigger="click" height="500px" :autoplay="false">

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 1</div>
                        <div class="news-h">Support services</div>
                        <div class="news-sum">Although open source software is free, ancillary products and value-added services can be provided in the
                             form of training, consulting, or extension development around open source products.<br><br>
                             <b>Characteristics: </b>Service providers do not need to own the original copyright of open source software; 
                             The support services surrounding the open source software are not just provided by the same company; 
                             The business lacks scalability, typically 20-30% profit margins, to generate enough capital for continued innovation; 
                             The need for such complementary products or services will increase as open source software becomes more widely adopted.</div>
                        </div>
                    </el-carousel-item>

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 2</div>
                        <div class="news-h">Dual authorization</div>
                        <div class="news-sum">The commerciality of open source software is not only reflected in the fact that the software itself is a commodity, 
                            but also that the source code can become a commodity. Software is provided under two separate licenses, usually one version 
                            licensed under an open source license and the other under a commercial license, which allows the software to 
                            be used exclusively (or in combination with other proprietary software).<br><br>
                             <b>Characteristics: </b>Software vendors need to own the original copyright of open source software; This model is mainly aimed
                              at commercial "embedded" customers (when the user needs to embed open source software into their own commercial products).
                               Open source versions usually have Copyleft clauses (GPL-style), which can prevent competitors from getting free riders from 
                               accessing the source code. Commercial integration users who do not want to be bound by copyleft terms must purchase a commercial license.</div>
                        </div>
                    </el-carousel-item>

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 3</div>
                        <div class="news-h">Source of business</div>
                        <div class="news-sum">In this model, it uses two different licenses with time delays, the source code is publicly released and freely editable. 
                            However the user must pay to use it for a set period of time (such as three years), after which the license automatically changes to an open source license.<br><br>
                             <b>Characteristics: </b>Software vendors need to own the original copyright of open source software; This model can meet the needs of both 
                             open source community and open source commercial users. However, licensing restrictions that are too restrictive can hurt the community 
                             and too lax can hurt the business. For example, MariaDB in BSL-1.1(with GPL-2.0+) requires all derivative software to 
                             follow the same terms (i.e. four years after the first public release of a particular version of the licensed work, Open source with GPL-2.0+).</div>
                        </div>
                    </el-carousel-item>

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 4</div>
                        <div class="news-h">Open core</div>
                        <div class="news-sum">The core base code of the software is provided under an open source license (a lite version) and proprietary 
                            code under a commercial license, which may be packaged as a separate module or service connected to the open source 
                            base (a paid plug-in) or distributed as a paid version with the open source base (an enterprise version).<br><br>
                             <b>Characteristics: </b>Software vendors do not need to own the original copyright of open source software; The more useful 
                             the core product (usually a generic module or generic domain product), the greater the potential interest in the community; 
                             From an end-user perspective, an open core leads to vendor lock-in, which can have a potentially negative impact on attracting 
                             and maintaining developers; Prone to a competing forked product.</div>
                        </div>
                    </el-carousel-item>

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 5</div>
                        <div class="news-h">Open core + Mixed licenses</div>
                        <div class="news-sum">An improvement over the open core model, the same codebase contains both open source and proprietary code,
                             and users can choose to use only open source or both.<br><br>
                             <b>Characteristics: </b>Software vendors need to own the original copyright of open source software; The code is in the same code base, 
                             which is convenient for management and development, and convenient for users to upgrade to the paid mode without additional deployment; 
                             Allowing an outside community to make improvements to proprietary code subject to conventions of licenses. For example, 
                             CockroachDB adopted CCL(free)+CCL(paid), allowing users to view and modify the source code, but not to reuse code without Cockroach Labs' permission.</div>
                        </div>
                    </el-carousel-item>

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 6</div>
                        <div class="news-h">Additional restriction clauses</div>
                        <div class="news-sum">A restriction clause, such as Common Clause1.0, is attached to the open source license, which prohibits 
                            others from directly using the open source software for profit to promote their own business needs.<br><br>
                             <b>Characteristics: </b>Software vendors need to own the original copyright of open source software; Open source vendors still 
                             need to choose a basic master license; Additional clauses may be poorly defined and usually require court determination. 
                             For example, Common Clause is not approved by OSI. Therefore, after Common Clause is added, 
                             the software is no longer open source software in the traditional sense. Instead, it can only be said that source code is source available.</div>
                        </div>
                    </el-carousel-item>

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 7</div>
                        <div class="news-h">Software as a Service</div>
                        <div class="news-sum">The service is provided over the Internet using open source software, but the software is not distributed to their users.<br><br>
                             <b>Characteristics: </b>Service providers do not need to own the original copyright of open source software; SaaS is not directly 
                             related to open source, but it can incorporate open source components or use open source software directly.</div>
                        </div>
                    </el-carousel-item>

                    <el-carousel-item>
                        <div style="margin-left: 20px">
                        <div class="category">Category 8</div>
                        <div class="news-h">Advertising or royalties</div>
                        <div class="news-sum">Companies can also generate revenue through advertising partnerships, brand licensing, and 
                            sales of business software, such as Mozilla's partnership with Yahoo to make Yahoo the default search engine in its Firefox browser.</div>
                        </div>
                    </el-carousel-item>

                    

                    </el-carousel>
                    </el-col>
                
                </el-row>
            </el-card>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            slide: 0
        }
    }
}
</script>

<style>
el-card {
    /* border-radius: 5%; */
    box-shadow: 13px 12px 2px 1px rgb(64 28 28 / 20%);
    border-color: #979797;
}

.title {
    color: #383841a6;
}

.el-carousel__item{
    background: #d5dbe3;
}

.category {
    font-size: 60px;
    font-weight: bold;
    color: black;
    font-family: Georgia, 'Times New Roman', Times, serif;
    text-align: left;
}

.news-h {
    font-size:35px; 
    font-weight: bold; 
    line-height: 1.4; 
    height:2em; 
    overflow: hidden; 
    margin-bottom: 0.1em;
    text-align: left;
    font: italic 2em Georgia, serif
}

.news-sum {
    line-height: 1.8; 
    /* height:300px;  */
    overflow: hidden; 
    color:#666;
    text-indent:20pt;
    text-align: left;
}

.news-sum b {
    font-family: Comic Sans MS, Comic Sans, cursive;
    font-size: 20px;
}
</style>