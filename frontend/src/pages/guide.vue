<template>
    <div>
        <div>
            <el-card style="width: 1550px; display: inline-block; margin-top: 30px;">
                <p style="font-size: 25px;color:blue;font-family:Comic Sans MS, Comic Sans, cursive;">If you want to know what type of licenses is suitbale for you, you can read this guideline!</p>
                <el-card class="second-card">
                    <b-jumbotron>
                        <template #header class="header" style="text-align: left">Personal open source style</template>

                        <template #lead style="text-align: left">
                            Personal open source style reflects how developers view the use of open source software.
                        </template>
                        <hr class="my-4">
                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-1  style="width:400px">Tip 1: Support
                                    continuous sharing.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-1" accordion="my-accordion" role="tabpanel">
                                <!-- <b-collapse id="accordion-1" visible accordion="my-accordion" role="tabpanel"></b-collapse> -->
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">Restricted open
                                        source licenses allow users to
                                        freely use, copy, modify and distribute software,
                                        but redistributing modified derivative software usually requires licensing under
                                        the same
                                        open source license
                                        (or a compatible open source license) to ensure continued open source.
                                    </b-card-text>

                                </b-card-body>
                            </b-collapse>
                        </b-card>

                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-2  style="width:400px">Tip 2: Support
                                    User rights.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-2" accordion="my-accordion" role="tabpanel">
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">Permissive open
                                        source licenses allow users to freely use,
                                        copy, modify and distribute software, and redistributing
                                        modified software that allows users to re-license, or even close the source. Users
                                        have more
                                        autonomy.</b-card-text>
                                </b-card-body>
                            </b-collapse>
                        </b-card>

                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-3 style="width:400px">Tip 3: Put
                                    into the public domain.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-3" accordion="my-accordion" role="tabpanel">
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">By placing
                                        software in the public domain, the
                                        author gives up copyright protection on the software, and
                                        anyone can use and modify it for free, or even remove the author's name as his
                                        or her own
                                        work.</b-card-text>
                                </b-card-body>
                            </b-collapse>
                        </b-card>

                    </b-jumbotron>
                </el-card>
                <el-card class="second-card">
                    <b-jumbotron>
                        <template #header class="header" style="text-align: left">Open source business
                            pattern</template>

                        <template #lead style="text-align: left">
                            Although open source is a superior development pattern,
                            there is no guarantee that every piece of software will make enough money from the open
                            source business pattern.
                            The open source license is the primary legal tool for open source software, and the wrong
                            choice can lead to
                            loss of revenue or even loss of control over software development.
                        </template>

                        <hr class="my-4">
                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-1 style="width:400px">Tip 1: Expand
                                    the user base.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-1" accordion="my-accordion" role="tabpanel">
                                <!-- <b-collapse id="accordion-1" visible accordion="my-accordion" role="tabpanel"></b-collapse> -->
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">The business
                                        requirements of business models such as
                                        support services and open core depend on a wide user base.
                                        The main difference between the permissive open source license and the restricted
                                        open source
                                        license is that the permissive open source
                                        license allows users to integrate the open source code into their products,
                                        rather than
                                        having to open source the code, so the
                                        permissive open source license is more friendly to business users. Especially if you
                                        want people
                                        to use your software for the
                                        commercial Internet of Things, then you're better off not choosing GPL-3.0(or a
                                        variant)
                                        because most users won't adopt it
                                        due to its terms regarding installation information.
                                    </b-card-text>

                                </b-card-body>
                            </b-collapse>
                        </b-card>

                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-2 style="width:400px">Tip 2: Reduce
                                    peer competition.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-2" accordion="my-accordion" role="tabpanel">
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">The source code
                                        of software is always one of the core
                                        values of software manufacturers.
                                        Although Fork can encourage innovation, it will also lead to the split and
                                        potential
                                        competition among developers.
                                        Restricted open source license requires different degrees of open source code
                                        for the
                                        release of derivative software,
                                        which reduces the opportunities for competitors to make private products by
                                        using open
                                        source software to some extent, thus reducing peer competition.</b-card-text>
                                </b-card-body>
                            </b-collapse>
                        </b-card>

                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-3 style="width:400px">Tip 3: Control
                                    product development.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-3" accordion="my-accordion" role="tabpanel">
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">How to
                                        effectively control the development
                                        direction of software is of strategic significance to open source manufacturers.
                                        Restricted open source license can reduce the bifurcation of code, and all the
                                        developed
                                        content can be retained, which is
                                        helpful to master the trend of software development. Open source vendors can
                                        also gain
                                        sufficient control over the
                                        software by participating in open source software decisions such as becoming a
                                        PMC or
                                        signing additional agreements such as CLA.</b-card-text>
                                </b-card-body>
                            </b-collapse>
                        </b-card>

                    </b-jumbotron>
                </el-card>
                <el-card class="second-card">
                    <b-jumbotron>
                        <template #header class="header" style="text-align: left">Development of project
                            community</template>

                        <template #lead style="text-align: left">
                            As a legal mechanism and incentive mechanism, the open source license is the foundation for
                            community cooperation.
                            The choice of license may influence the participation and contribution of the community.
                            Different stakeholders in different
                            open source projects have different understandings of the license terms and conditions. 
                            <!-- When
                            an open source project adopts
                            a particular open source license under certain conditions, this choice may be preferred by
                            some individuals and companies, while others may not, so they decide not to participate in
                            and contribute to a particular
                            project, thereby impacting its future development and its community. For projects looking to
                            build their own community,
                            what kind of community to attract is a consideration. Generally speaking, in the development
                            phase, working with the
                            community to write and improve the software code is the main goal, while in the release
                            phase, the main goal is to
                            expand the user base of the software and generate positive network effects. -->
                        </template>

                        <hr class="my-4">
                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-1  style="width:400px">Tip 1: Users.
                                    </b-button>
                            </b-card-header>
                            <b-collapse id="accordion-1" accordion="my-accordion" role="tabpanel">
                                <!-- <b-collapse id="accordion-1" visible accordion="my-accordion" role="tabpanel"></b-collapse> -->
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">One way open
                                        source software gains potential value is by allowing other
                                        programs to rely on it, i.e.
                                        cumulative improvements and integrations in other software products. Widespread
                                        adoption of
                                        open source software can
                                        not only help expand the user base, but also bring economic opportunities and
                                        increased
                                        reputation. The type of software
                                        and the type of open source license it uses affects its reuse. Programs higher
                                        up on the
                                        software stack depend on the
                                        functionality of programs lower down the stack. Open source licenses determine
                                        what a
                                        program can do and whether it
                                        can be combined with other programs. Permissive open source licenses allow users a
                                        high degree
                                        of freedom to use and reuse code,
                                        allow the choice of downstream licenses (sublicense), and there is no pressure
                                        on any user.
                                        The more reciprocal open source
                                        licenses are, the more difficult it is to produce proprietary products from
                                        derivative
                                        products, reducing the appeal to
                                        commercial users who want to produce proprietary derivative software. Studies
                                        have shown
                                        that software projects with high
                                        commercial value are more likely to be released under unrestricted licenses.
                                    </b-card-text>

                                </b-card-body>
                            </b-collapse>
                        </b-card>

                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-2  style="width:400px">Tip 2:
                                    Contributors.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-2" accordion="my-accordion" role="tabpanel">
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">Open source
                                        software projects rely on the continued
                                        contributions of developers to sustain large-scale
                                        development and steady growth, and OSS developers work on a completely
                                        voluntary,
                                        non-contractual, non-commissioned basis,
                                        with motivation believed to play a significant role in their behavior.
                                        Intrinsically
                                        motivated contributors, who are motivated
                                        to participate in open source projects by intrinsic incentives such as work
                                        challenges and
                                        peer recognition, generally prefer modest
                                        restrictions, and restricted licenses keep the software open and attract
                                        contributors with a
                                        "free software" philosophy. Extrinsic
                                        motivated contributors who participate in open source projects not only for
                                        intrinsic
                                        motivation, but also for extrinsic motivation
                                        such as commercialization potential, reputation, and status. A permissive open source
                                        license is
                                        business-friendly, and a high number of
                                        users allows their skills to be better demonstrated.</b-card-text>
                                </b-card-body>
                            </b-collapse>
                        </b-card>

                        <b-card no-body class="mb-1">
                            <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block v-b-toggle.accordion-3  style="width:400px">Tip 3: Partner
                                    or competitor.</b-button>
                            </b-card-header>
                            <b-collapse id="accordion-3" accordion="my-accordion" role="tabpanel">
                                <b-card-body>
                                    <b-card-text style="width:600px;margin-left:auto;margin-right:auto;text-align:justify;text-align-last: center;">Open source
                                        licenses are the primary tool for gaining
                                        the trust of such potential members. Restricted open source licenses can provide
                                        such
                                        contributors with some assurance that their (often) unpaid work will
                                        remain open and not be exploited directly for commercial purposes, whereas under
                                        non-restrictive licenses,
                                        developers know that they may have to pay a price for future use of the
                                        resulting software.
                                        For example, some studies have shown that
                                        companies in the embedded systems field may prefer to participate in open source
                                        projects
                                        that provide software under the GPL.
                                        Some enterprises choose open source licenses like the GPL to attract interest
                                        from partners
                                        or competitors.
                                        Another interesting move that some software companies use to motivate employees
                                        is to
                                        guarantee in their employment contracts
                                        that all software they produce for the company will be released under an open
                                        source
                                        license.</b-card-text>
                                </b-card-body>
                            </b-collapse>
                        </b-card>


                    </b-jumbotron>
                </el-card>
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

<style scoped>
.second-card {
    width: 1400px;
    margin-top: 40px;
    display: inline-block;
    /* background: #d5dbe3; */
}

.display-3 {
    text-align: left;
    font-size: 30px;
}

.lead {
    text-align: left;
    font-family:Comic Sans MS, Comic Sans, cursive;
    font-size: 20px;
}

.tip {
    text-align: left;
    font-family: Comic Sans MS, Comic Sans, cursive;
    font-size: 18px;
}

.carousel-card {
    box-shadow: 13px 12px 2px 1px rgb(64 28 28 / 20%);
    border-color: #979797;
    /* height: 550px; */
    width: 1400px;
    position: relative;
    display: inline-block;
    /* margin-top: 20px; */
}

.second-carousel-item {
    background: #d5dbe3;
}

.first-carousel>.el-carousel__container {
    height: 900px;
}

.category {
    font-size: 25px;
    font-weight: bold;
    color: black;
    font-family: Georgia, 'Times New Roman', Times, serif;
    text-align: left;
}

.news-h {
    font-size: 20px;
    font-weight: bold;
    line-height: 1.4;
    height: 2em;
    overflow: hidden;
    margin-bottom: 0.1em;
    text-align: left;
    font: italic 2em Georgia, serif
}

.news-sum {
    line-height: 1.8;
    /* height:300px;  */
    overflow: hidden;
    color: #666;
    text-indent: 20pt;
    text-align: left;
}

.news-sum b {
    font-family: Comic Sans MS, Comic Sans, cursive;
    font-size: 15px;
}
</style>