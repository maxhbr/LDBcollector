<template>
    <div id="term-comparision" style="overflow-y: scroll; height: 515px;">
        <el-table :data="license_terms" fit style="width: 100%;" :cell-class-name="cell_class" border>
            <el-table-column prop="license" label="License"></el-table-column>

            <el-table-column prop="info" label="Info">
                <template slot-scope="scope"><span>{{scope.row.info}}</span></template>
            </el-table-column>

            <el-table-column prop="preamble" label="Preamble" width="100">
                <template slot-scope="scope"><span>{{scope.row.preamble}}</span></template>
            </el-table-column>

            <el-table-column prop="define" label="Define">
                <template slot-scope="scope"><span>{{scope.row.define}}</span></template>
            </el-table-column>

            <el-table-column prop="copyright" label="Copyright" width="100">
                <template slot-scope="scope"><span>{{scope.row.copyright}}</span></template>
            </el-table-column>

            <el-table-column prop="patent" label="Patent">
                <template slot-scope="scope"><span>{{scope.row.patent}}</span></template>
            </el-table-column>

            <el-table-column prop="trademark" label="Trademark" width="100">
                <template slot-scope="scope"><span>{{scope.row.trademark}}</span></template>
            </el-table-column>

            <el-table-column prop="copyleft" label="Copyleft">
                <template slot-scope="scope"><span>{{scope.row.copyleft}}</span></template>
            </el-table-column>

            <el-table-column prop="interaction" label="Interaction" width="100">
                <template slot-scope="scope"><span>{{scope.row.interaction}}</span></template>
            </el-table-column>

            <el-table-column prop="modification" label="Modification" width="110">
                <template slot-scope="scope"><span>{{scope.row.modification}}</span></template>
            </el-table-column>

            <el-table-column prop="retain_attr" label="Retain attribution" width="100">
                <template slot-scope="scope"><span>{{scope.row.retain_attr}}</span></template>
            </el-table-column>

            <el-table-column prop="enhance_attr" label="Enhance attribution" width="100">
                <template slot-scope="scope"><span>{{scope.row.enhance_attr}}</span></template>
            </el-table-column>

            <el-table-column prop="patent_term" label="Patent term" width="100">
                <template slot-scope="scope"><span>{{scope.row.patent_term}}</span></template>
            </el-table-column>

            <el-table-column prop="vio_term" label="Vio term">
                <template slot-scope="scope"><span>{{scope.row.vio_term}}</span></template>
            </el-table-column>

            <el-table-column prop="disclaimer" label="Disclaimer" width="100">
                <template slot-scope="scope"><span>{{scope.row.disclaimer}}</span></template>
            </el-table-column>

            <el-table-column prop="law" label="Law">
                <template slot-scope="scope"><span>{{scope.row.law}}</span></template>
            </el-table-column>

            <el-table-column prop="instruction" label="Instruction" width="100">
                <template slot-scope="scope"><span>{{scope.row.instruction}}</span></template>
            </el-table-column>

            <el-table-column prop="vio_term" label="Vio term">
                <template slot-scope="scope"><span>{{scope.row.vio_term}}</span></template>
            </el-table-column>

            <el-table-column prop="compatible_version" label="Compatible version" width="100">
                <template slot-scope="scope"><span>{{scope.row.compatible_version}}</span></template>
            </el-table-column>

            <el-table-column prop="secondary_license" label="Secondary license" width="95">
                <template slot-scope="scope"><span>{{scope.row.secondary_license}}</span></template>
            </el-table-column>

            <el-table-column prop="gpl_combine" label="GPL combine" width="100">
                <template slot-scope="scope"><span>{{scope.row.gpl_combine}}</span></template>
            </el-table-column>
        </el-table>
        <!-- <b-button variant="success" @click="term_compare" style="margin-top: 20px">Submit</b-button> -->
    </div>

</template>

<script>
export default {
    name: 'compare',
    props : ["licenses"],
    data() {
        return {
            // licenses: ["MIT","MulanPSL-2.0","GPL-2.0-only"],
            specific_terms: {
                copyleft: ['公共领域', '模糊授予版权', '明确授予版权'],
                copyright: ['示宽松型', '文件级弱限制型', '库级弱限制型', '限制型']
            },
            license_terms: [
                {
                    // license: '',
                    // info: '',
                    // preamble: '',
                    // define: '',
                    // copyright: '',
                    // patent: '',
                    // trademark: '',
                    // copyleft: '',
                    // interaction: '',
                    // modification: '',
                    // retain_attr: '',
                    // enhance_attr: '',
                    // acceptance: '',
                    // patent_term: '',
                    // vio_term: '',
                    // disclaimer: '',
                    // law: '',
                    // instruction: '',
                    // compatible_version: '',
                    // secondary_license: '',
                    // gpl_combine: ''
                }
            ]
        }
    },

    mounted() {
        this.term_compare();
    },

    methods: {
        term_compare() {
            var temp = [];
            console.log("term")
            console.log(this.licenses);
            for (const license of this.licenses) {
                temp.push(license.name);
            }
            console.log(temp)

            const config = {
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            this.axios.post('/api/compare', {'recommend_list': temp}, config)
            .then(res => {
                console.log(res.data);
                this.license_terms = res.data;
            }).catch(res => {
                console.log('wrong');
            })
        },

        cell_class({row, column, rowIndex, columnIndex}) {
            // console.log(this.license_terms[rowIndex][column.property]);

            if (this.license_terms[rowIndex][column.property] == 1) {
                return "icon-success"
            }

            if (this.license_terms[rowIndex][column.property] == 0) {
                return "icon-wrong"
            }
        }
    },

}
</script>

<style>
.cell {
    text-align: center;
}

.icon-success > .cell, .icon-wrong > .cell {
    position: relative;
    font-size: 0;
    height: 20px;
    width: auto;
    margin-left: 15px;
}

.icon-success > .cell::before{
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

.icon-wrong > .cell::before{
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