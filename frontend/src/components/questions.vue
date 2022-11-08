<template>
    <div>
        <div id="license_question1" class="terms_question_area">
						<div><p class="question-font">您是否支持“衍生作品采用其他许可证重新分发”的态度？</p></div>
						<div>
							<p class="instruction-font">说明：不同类型的开源许可证反映了您如何看待开源软件（或其他作品）的使用问题，<b>宽松型开源许可证</b>允许用户自由地使用、复制、修改和分发软件，
									且重新分发修改后的软件允许用户重新选择许可方式，甚至闭源，用户拥有更多的自主权；<b>限制型开源许可证</b>允许用户自由地使用、复制、修改和分发软件，
									但重新分发的软件通常须要在相同的开源许可证（或其兼容的开源许可证）下授权，以确保软件的持续开源;将软件放置<b>公共领域</b>，意味着您放弃对软件的版权保护，
									任何人都可以无偿地使用和修改,甚至可以删除您的名字视为其自己的作品。
							</p>
						</div>
						<div class="radio-area">
							<!-- <div><label><input name="question1" type="radio" style="outline:none" value="宽松型开源许可证" />A、支持，宽松型开源许可证</label></div>
							<div><label><input name="question1" type="radio" style="outline:none" value="限制型开源许可证" />B、不支持，限制型开源许可证</label></div>
							<div><label><input name="question1" type="radio" style="outline:none" value="公共领域许可证" />C、无所谓，将作品放置公共领域</label></div> -->
                            <b-form-group>
                            <b-form-radio v-model="selected[0]" value="1">A、支持，宽松型开源许可证</b-form-radio>
                            <b-form-radio v-model="selected[0]" value="2">B、不支持，限制型开源许可证</b-form-radio>
                            <b-form-radio v-model="selected[0]" value="3">C、无所谓，将作品放置公共领域</b-form-radio>
                            </b-form-group>
						</div>
					</div>
					<div id="license_question2" class="terms_question_area" style="display:none;">
						<div><p class="question-font">您对衍生作品分发的限制性强弱的态度？</p></div>
						<div><p class="instruction-font">说明：开源许可证的”限制性“条款也称”copyleft条款“。<b>“强限制型”</b>许可证要求对软件的修改和扩展后的分发都必须按照获得该软件的许可证进行开源，如GPL2.0；<b>“弱限制型”</b>许可证要求对软件修改后的重新分发必须按照获得该软件的许可证进行授权，
									但允许将代码集成到自己的软件中，而不必使整个代码库开源，合并这些软件的大型作品可以成为私有作品，<b>”文件级/模块级/库级“</b>是指许可证的copyleft范围，如MPL-2.0是弱限制型开源许可证，只要专有代码与MPL-2.0授权代码位于不同文件，即可隔离传染等。</p></div>
						<div class="radio-area">
							<!-- <div><label><input name="question2" type="radio" style="outline:none" value="文件级__弱限制型开源许可证" />A、文件级__弱限制型开源许可证</label></div>
							<div><label><input name="question2" type="radio" style="outline:none" value="库级__弱限制型开源许可证" />B、库级__弱限制型开源许可证</label></div>
							<div><label><input name="question2" type="radio" style="outline:none" value="强限制型开源许可证" />C、强限制型开源许可证</label></div> -->
                            <b-form-group v-slot="{ ariaDescribedby }">
                            <b-form-radio v-model="selected[1]" value="1">A、文件级__弱限制型开源许可证</b-form-radio>
                            <b-form-radio v-model="selected[1]" value="2">B、库级__弱限制型开源许可证</b-form-radio>
                            <b-form-radio v-model="selected[1]" value="3">C、强限制型开源许可证</b-form-radio>
                            </b-form-group>
						</div>
					</div>
					<div id="license_question3" class="terms_question_area" style="display:none;">
						<div><p class="question-font">您是否明确“授予专利权”？</p></div>
						<div><p class="instruction-font">说明：软件的可专利性是开源软件正在面临的威胁之一，开源软件中可能包含软件专利，一些开源软件许可证未提及专利授权，
							尽管这可能并不意味着它们不授予专利权（即默示授予专利），然而明确的专利授权有利于保护开源软件的用户免受专利诉讼，尤其是面向一些拥有大量专利组合和其他专利组合风险的企业用户，
							他们普遍很重视专利权的明确授予。</p></div>
						<div class="radio-area">
							<!-- <div><label><input name="question3" type="radio" style="outline:none" value="不提及专利权" />A、不提及专利权</label></div>
							<div><label><input name="question3" type="radio" style="outline:none" value="明确授予专利权" />B、明确授予专利权</label></div>
							<div><label><input name="question3" type="radio" style="outline:none" value="明确不授予专利权" />C、明确不授予专利权</label></div> -->
                            <b-form-radio v-model="selected[2]" value="1">A、不提及专利权</b-form-radio>
                            <b-form-radio v-model="selected[2]" value="2">B、明确授予专利权</b-form-radio>
                            <b-form-radio v-model="selected[2]" value="3">C、明确不授予专利权</b-form-radio>
						</div>
					</div>
					<div id="license_question4" class="terms_question_area" style="display:none;">
						<div><p class="question-font">您是否希望许可证中包含“反专利诉讼”条款？</p></div>
						<div><p class="instruction-font">说明：“反专利诉讼”是指任何提起“声称被许可方侵犯了其在许可作品中的专利权”等此类法律诉讼的人，将失去已经授予其在该许可证中的权利。
							“反专利诉讼”的目的是阻止人们提起关于许可作品的专利诉讼，保护开源软件的用户规避陷入专利诉讼的风险。</p></div>
						<div class="radio-area">
							<!-- <div><label><input name="question4" type="radio" style="outline:none" value="包含反专利诉讼条款" />A、包含反专利诉讼条款</label></div>
							<div><label><input name="question4" type="radio" style="outline:none" value="不包含反专利诉讼条款" />B、不包含反专利诉讼条款</label></div> -->
                            <b-form-radio v-model="selected[3]" value="1">A、包含反专利诉讼条款</b-form-radio>
                            <b-form-radio v-model="selected[3]" value="2">B、不包含反专利诉讼条款</b-form-radio>
						</div>
					</div>
					<div id="license_question5" class="terms_question_area" style="display:none;">
						<div><p class="question-font">您是否明确商标权<b style="color:red">限制</b>？</p></div>
						<div><p class="instruction-font">说明：开源软件中可能包含商标，商标权许可将意味着商标所有人失去其对商标的权利，因此，尽管一些开源软件许可证未提及商标权，在使用开源软件时默示不授予商标权；
							还有一些许可证明确不授予商标权，或禁止使用作者的名字来推广软件或销售服务等背书、广告或其他特定行为。
							明确“不授予商标权”有利于保护您的商标合法权益，然而早期出现的一些流行使用的开源许可证可能没有明确包含此条款，例如MIT、BSD-2-Clause、GPL-2.0、GPL-3.0等，
							您也可以通过附加条款、签署其他协议等方式来明确对商标权的限制。</p></div>
						<div class="radio-area">
							<!-- <div><label><input name="question5" type="radio" style="outline:none" value="不提及商标权" />A、不提及商标权</label></div>
							<div><label><input name="question5" type="radio" style="outline:none" value="明确不授予商标权" />B、明确不授予商标权</label></div> -->
                            <b-form-radio v-model="selected[4]" value="1">A、不提及商标权</b-form-radio>
                            <b-form-radio v-model="selected[4]" value="2">B、明确不授予商标权</b-form-radio>
						</div>
					</div>
					<div id="license_question6" class="terms_question_area" style="display:none;">
						<div><p class="question-font">您对用户使用开源软件或其衍生软件进行“网络交互”的态度？</p></div>
						<div><p class="instruction-font">说明：“网络交互”是指向用户使用开源软件为他人提供在线服务等行为，即使软件的物理副本并未被分发。
									”网络交互视为分发“是指用户使用开源软件或其衍生软件进行”网络交互“，须按照获得该软件的许可证授权并分发其源代码，
									例如在云中使用AGPL-3.0授权的软件提供在线服务也须要发布其源代码。</p></div>
						<div class="radio-area">
							<!-- <div><label><input name="question6" type="radio" style="outline:none" value="网络部署公开源码" />A、网络交互公开源码</label></div>
							<div><label><input name="question6" type="radio" style="outline:none" value="网络部署不须公开源码" />B、网络交互不须公开源码</label></div> -->
                            <b-form-radio v-model="selected[5]" value="1">A、网络交互公开源码</b-form-radio>
                            <b-form-radio v-model="selected[5]" value="2">B、网络交互不须公开源码</b-form-radio>
						</div>
					</div>
					<div id="license_question7" class="terms_question_area" style="display:none;">
						<div><p class="question-font">您是否希望用户为其制作的衍生软件添加“修改说明”？</p></div>
						<div><p class="instruction-font">说明：“修改说明”是指要求用户在分发其修改后的软件（衍生软件）时，必须标记修改内容、日期、修改作者等信息。
							“修改说明”有利于增强开源软件贡献者的可见性和软件的可维护性；然而，用户可能因为疏忽导致许可证违规；且该条款的存在与否将影响开源许可证的兼容性。</p></div>
						<div class="radio-area">
							<!-- <div><label><input name="question7" type="radio" style="outline:none" value="包含修改说明条款" />A、是，包含”修改说明“</label></div>
							<div><label><input name="question7" type="radio" style="outline:none" value="不包含修改说明条款" />B、否，不包含“修改说明”</label></div> -->
                            <b-form-radio v-model="selected[6]" value="A">A、是，包含“修改说明”</b-form-radio>
                            <b-form-radio v-model="selected[6]" value="B">B、否，不包含“修改说明”</b-form-radio>
						</div>
					</div>
				<b-button variant="success" @click="previous_q" id="previous-button">Previous question</b-button>
                <b-button variant="success" @click="next_q" id="next-button">Next question</b-button>
                <b-button variant="success" @click="skip_q" id="skip-button" style="display: none">Skip</b-button>
                <b-button variant="outline-primary" @click="submit_q" id="upload-button">Submit</b-button>
    </div>
</template>

<script>
import $ from 'jquery'
export default {
    name: 'questions',
    data() {
        return {
            selected: ['', '', '', '', '', '', ''],
            number: 1
        }
    },

	mounted() {
		$('#upload-button').hide();
		$('#previous-button').hide();
	},

    methods: {
		previous_q() {
			if (this.number > 1) {
				if (this.number == 2) {
					$('#next-button').show();
					$('#previous-button').hide();
				}

				if (this.number == 7) {
					$('#next-button').show();
					$('#upload-button').hide();
				}

                var cur = '#' + 'license_question' + String(this.number--);
                var previous = '#' + 'license_question' + String(this.number);
                $(cur).hide();
                $(previous).show();
            } 
		},

        next_q() {
            if (this.number < 7) {
				if (this.number == 6) {
					$('#next-button').hide();
					$('#upload-button').show();
				}

                var cur = '#' + 'license_question' + String(this.number++);

				if (this.number == 2 && this.selected[0] == '2') {
					this.number++;
				}

                var next = '#' + 'license_question' + String(this.number);
                $(cur).hide();
                $(next).show();
				$('#previous-button').show()
            }
        },

		skip_q() {
			if (this.number < 7) {
                var cur = '#' + 'license_question' + String(this.number++);
                var next = '#' + 'license_question' + String(this.number);
                $(cur).hide();
                $(next).show();
            }
		},

		submit_q() {
			var data = {'answer': this.selected};
			const config = {
				headers: {
					'Content-Type': 'application/json'
				}
			};
			this.axios.post('/api/choice', data, config)
			.then(res => {
				if (res.status == 200){
					console.log('success');
					console.log(res.data);
					this.$emit("question_over", res.data)
				} else {
					console.log('wrong');
				}
			}).catch( res => {
				console.log('wrong');
			})
		},

		ariaDescribedby() {

		}
    }
}
</script>

<style>
.terms_question_area{
    height:375px;
    border-top: 0;
	text-align: left;
}

.question-font{
    width: auto;
    margin-left: 15px;
    float: left;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 20px;
    line-height: 25px;
    color: #666;
    font-weight: 550;
    margin-bottom: 3px;
}

.instruction-font{
    width: auto;
    margin-left: 15px;
    float: left;
    font-family: Georgia, Arial, Sans-Serif;
    font-size: 15px;
    color: #5f5f5f;
    line-height: 25px;
    border-bottom:1px solid #ddd;
    margin-bottom:20px;
}

.radio-area{
    float: left;
    margin-left:20px;
    font-size:18px;
    font-weight:200;
    line-height: 35px;
}
</style>