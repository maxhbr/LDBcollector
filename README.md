# LicenseRec

## 更新
📢 *LicenseRec V2.0.0 正式上线！增加了包括精确到包版本的合规性分析、基于SMT-Solver的许可证不兼容消解等功能！*


## 简介
这是[北京大学开源分析实验室](https://github.com/osslab-pku/)研发的工具，以帮助开源许可证合规性分析与开源许可证的选择.

LicenseRec是一个可证合规性分析与开源许可证推荐工具，帮助开发者为他们的开源软件项目进行合规性分析和选择一个最佳许可证。
LicenseRec对开源软件项目的代码和依赖关系（包括直接依赖与间接依赖）进行细粒度的许可证合规性分析，针对不兼容情况，使用基于约束求解的方法给出了最小代价的不兼容消解方案。合规性分析与不兼容消解功能可在[https://licenserec.com/#/compliance](https://licenserec.com/#/compliance)使用。
LicenseRec在合规性分析的基础上，通过一个交互式的向导来帮助开发者选择最佳的许可证，该向导有三个方面的指引：个人开放源码风格、商业模式和社区发展。推荐功能可在[https://licenserec.com/#/rec](https://licenserec.com/#/rec)使用。

该工具可演示视频在[video.licenserec.com](https://video.licenserec.com/)。该工具的推荐功能已发表在ICSE'23的DEMO Track上，论文参见：[LicenseRec: Knowledge based Open Source License Recommendation for OSS Projects](https://ieeexplore.ieee.org/abstract/document/10172799)，合规性分析与不兼容消减方法已发表在ASE'23上，论文参见：[Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem](https://ieeexplore.ieee.org/abstract/document/10298475)。

快来上传你的项目，在[licenserec.com](https://licenserec.com/)上进行合规性分析并挑选最佳的开源许可证吧!

## 安装

LicenseRec可以通过两种方式安装：使用Docker或手动。查看[DEPLOY.md](./DEPLOY.md)中的部署说明。

## 知识库
[开源许可证知识库（knowledge_base）](./knowledge_base/)文件夹下，包含了开源许可证兼容性矩阵、条款特征矩阵、兼容性判定方法等资料。包括为机器阅读而建立的文件（即本工具的输入），以及为人类理解而建立的文件（具有更多的解释）。

## 许可证和鸣谢

LicenseRec是根据[木兰公共许可证v2](http://license.coscl.org.cn/MulanPubL-2.0)授权的。详情见[LICENSE](LICENSE)。

LicenseRec依赖于以下开源项目。

* [scancode-tookit](https://github.com/nexB/scancode-toolkit)采用[Apache-2.0](https://opensource.org/licenses/Apache-2.0)授权。（我们增加和修改了一些检测规则。）
* [depend](https://github.com/multilang-depends/depends) 采用[MIT](https://opensource.org/licenses/MIT)授权。

## 引用
```
@INPROCEEDINGS{licenserec,
  author={Xu, Weiwei and Wu, Xin and He, Runzhi and Zhou, Minghui},
  booktitle={2023 IEEE/ACM 45th International Conference on Software Engineering: Companion Proceedings (ICSE-Companion)}, 
  title={LicenseRec: Knowledge based Open Source License Recommendation for OSS Projects}, 
  year={2023},
  pages={180-183},
  doi={10.1109/ICSE-Companion58688.2023.00050}}

@inproceedings{SILENCE2023,
  title={Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem},
  author={Xu, Weiwei and He, Hao and Gao, Kai and Zhou, Minghui},
  booktitle={2023 38th IEEE/ACM International Conference on Automated Software Engineering (ASE)},
  pages={178--190},
  year={2023},
  organization={IEEE}
}
```
## News
📢 *LicenseRec V2.0.0 is officially launched! New features include compliance analysis accurate to package versions and license incompatibility remediation based on SMT-Solver!*

## Introduction


LicenseRec is a license compliance analysis and open-source license recommendation tool that helps developers perform compliance analysis and select the optimal license for their open-source software projects.

LicenseRec conducts fine-grained license compliance analysis on the code and dependencies (including direct and indirect dependencies) of open-source software projects. For incompatibility cases, it provides a minimum-cost incompatibility remediation solution using a constraint-solving based method. The compliance analysis and incompatibility remediation functions can be accessed at [https://licenserec.com/#/compliance](https://licenserec.com/#/compliance).

Based on the compliance analysis, LicenseRec helps developers choose the best license through an interactive wizard. This wizard provides guidance in three aspects: personal open-source style, business model, and community development. The recommendation function can be used at [https://licenserec.com/#/rec](https://licenserec.com/#/rec).

A demonstration video of the tool is available at [video.licenserec.com](https://video.licenserec.com/). The recommendation feature of this tool has been published in the DEMO Track of ICSE'23, and the paper can be found here: [LicenseRec: Knowledge based Open Source License Recommendation for OSS Projects](https://ieeexplore.ieee.org/abstract/document/10172799). The compliance analysis and incompatibility remediation method have been published at ASE'23, and the paper can be found here: [Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem](https://ieeexplore.ieee.org/abstract/document/10298475).

Come and upload your project to perform compliance analysis and select the best open-source license at [licenserec.com](https://licenserec.com/)!

## Installation

LicenseRec can be installed in two ways: using Docker or manually. Check deployment instructions in [DEPLOY.md](./DEPLOY.md).

## Knowledge base
The [knowledge_base](./knowledge_base/) folder contains information on open source license compatibility matrix, term feature matrix, compatibility judgment method, and so on. There are two groups of files: files for machine reading (i.e, input for this tool), and files for human understanding (with more explanation about license compatibility).

## License and Acknowledgements

LicenseRec is licensed under [MulanPubL-2.0](http://license.coscl.org.cn/MulanPubL-2.0). See [LICENSE](LICENSE) for details.

LicenseRec relies on the following open source projects:

* [scancode-tookit](https://github.com/nexB/scancode-toolkit) is licensed under [Apache-2.0](https://opensource.org/licenses/Apache-2.0).(We added and modified some detection rules.)
* [depends](https://github.com/multilang-depends/depends) is licensed under [MIT](https://opensource.org/licenses/MIT).

## Citation

For citing, please use following BibTex citation:
```
@INPROCEEDINGS{licenserec,
  author={Xu, Weiwei and Wu, Xin and He, Runzhi and Zhou, Minghui},
  booktitle={2023 IEEE/ACM 45th International Conference on Software Engineering: Companion Proceedings (ICSE-Companion)}, 
  title={LicenseRec: Knowledge based Open Source License Recommendation for OSS Projects}, 
  year={2023},
  pages={180-183},
  doi={10.1109/ICSE-Companion58688.2023.00050}}

@inproceedings{SILENCE2023,
  title={Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem},
  author={Xu, Weiwei and He, Hao and Gao, Kai and Zhou, Minghui},
  booktitle={2023 38th IEEE/ACM International Conference on Automated Software Engineering (ASE)},
  pages={178--190},
  year={2023},
  organization={IEEE}
}
```
