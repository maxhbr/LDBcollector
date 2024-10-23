<template>
    <div id="term-comparision" style="height: 515px;">
        <el-table :data="license_terms" fit style="width: 100%;" :cell-class-name="cell_class" border height="500" empty-text="No data">
            <el-table-column prop="license" label="License" fixed></el-table-column>

            <el-table-column prop="info" label="Info">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.info}}</span></template>
            </el-table-column>

            <el-table-column prop="preamble" label="Preamble" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.preamble}}</span></template>
            </el-table-column>

            <el-table-column prop="define" label="Define">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.define}}</span></template>
            </el-table-column>

            <el-table-column prop="copyright" label="Copyright" width="200">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{specific_terms.copyright[scope.row.copyright+1]}}</span></template>
            </el-table-column>

            <el-table-column prop="patent" label="Patent" width="200">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{specific_terms.patent[scope.row.patent+1]}}</span></template>
            </el-table-column>

            <el-table-column prop="trademark" label="Trademark" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.trademark}}</span></template>
            </el-table-column>

            <el-table-column prop="copyleft" label="Copyleft" width="200">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{specific_terms.copyleft[scope.row.copyleft]}}</span></template>
            </el-table-column>

            <el-table-column prop="interaction" label="Interaction" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.interaction}}</span></template>
            </el-table-column>

            <el-table-column prop="modification" label="Modification" width="110">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.modification}}</span></template>
            </el-table-column>

            <el-table-column prop="retain_attr" label="Retain attribution" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.retain_attr}}</span></template>
            </el-table-column>

            <el-table-column prop="enhance_attr" label="Enhance attribution" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.enhance_attr}}</span></template>
            </el-table-column>

            <el-table-column prop="patent_term" label="Patent term" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.patent_term}}</span></template>
            </el-table-column>

            <el-table-column prop="vio_term" label="Vio term">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.vio_term}}</span></template>
            </el-table-column>

            <el-table-column prop="disclaimer" label="Disclaimer" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.disclaimer}}</span></template>
            </el-table-column>

            <el-table-column prop="law" label="Law">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.law}}</span></template>
            </el-table-column>

            <el-table-column prop="instruction" label="Instruction" width="100">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.instruction}}</span></template>
            </el-table-column>

            <el-table-column prop="vio_term" label="Vio term">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.vio_term}}</span></template>
            </el-table-column>

            <el-table-column prop="compatible_version" label="Compatible version" :width="compatible_width">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.compatible_version}}</span></template>
            </el-table-column>

            <el-table-column prop="secondary_license" label="Secondary license" :width="secondary_width">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.secondary_license}}</span></template>
            </el-table-column>

            <el-table-column prop="gpl_combine" label="GPL combine" :width="gpl_width">
                <template slot-scope="scope"><span style="word-break: keep-all;">{{scope.row.gpl_combine}}</span></template>
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
            compatible_width: 100,
            secondary_width: 100,
            gpl_width: 100,
            specific_terms: {
                copyright: ['Public domain', 'Grant copyright vaguely.', 'Grant copyright explicitly.'],
                copyleft: ['Permissive', 'File-level weakly restrictive', 'Library-level weakly restrictive', 'Restrictive'],
                patent: ['Do not grant patent rights.', 'Do not mention patent rights.', 'Grant patent rights explicitly.']
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
    },

    methods: {
        term_compare(val) {
            console.log(this.licenses);
            console.log(val);
            var temp = [];
            for (const license of val) {
                temp.push(license.name);
            }

            const config = {
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            this.axios.post('/api/compare', {'recommend_list': temp}, config)
            .then(res => {
                this.license_terms = res.data;
                // console.log(res.data);
                this.adjust_width();
            }).catch(res => {
                console.log('wrong');
            })
        },

        adjust_width() {
            var new_comp = 100;
            var new_sec = 100;
            var new_gpl = 100;

            for (const term of this.license_terms) {
                var len_comp = term.compatible_version.length * 5;
                var len_sec = term.secondary_license.length * 5;
                var len_gpl = term.gpl_combine.length * 5;
                new_comp = new_comp < len_comp  ? len_comp : new_comp;
                new_sec = new_sec < len_sec ? len_sec : new_sec;
                new_gpl = new_gpl < len_gpl ? len_gpl : new_gpl;
            }
            this.compatible_width = new_comp;
            this.secondary_width = new_sec;
            this.gpl_width = new_gpl;
        },

        cell_class({row, column, rowIndex, columnIndex}) {

            if (column.property != 'copyleft' && column.property != 'copyright' && column.property != 'patent') {
                if (this.license_terms[rowIndex][column.property] == 1) {
                    return "icon-success"
                } else if (this.license_terms[rowIndex][column.property] == 0) {
                    return "icon-wrong"
                } else {
                    return "special-column"
                }
            } else {
                return "special-column"
            }
        }
    },

}
</script>

<style>
.special-column > .cell {
    word-break: keep-all;
}

.el-table .cell {
    word-break: keep-all;
}

.el-table__row > * > .cell {
    word-break: keep-all;
}

.icon-success > .cell, .icon-wrong > .cell {
    position: relative;
    font-size: 0;
    height: 20px;
    width: auto;
    margin-left: 15px;
    /* word-break: keep-all; */
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