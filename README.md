# LicenseRec

这是[北京大学开源分析实验室](https://github.com/osslab-pku/)研发的工具，以帮助开源许可证的选择.

![Image text](https://github.com/osslab-pku/RecLicense/blob/1caf4372960a9a54cfcbfbbbdf9ee86ab922d61a/frontend/src/assets/tool.png)

## 简介

LicenseRec是一个开源许可证推荐工具，帮助开发者为他们的开源软件项目选择一个最佳许可证。
LicenseRec对开源软件项目的代码和依赖关系进行细粒度的许可证兼容性检查，并通过一个交互式的向导来帮助开发者选择最佳的许可证，该向导有三个方面的指引：个人开放源码风格、商业模式和社区发展。

该工具可在[licenserec.com](https://licenserec.com/)使用，演示视频在[video.licenserec.com](https://video.licenserec.com/)。该工具已发表在ICSE'23的DEMO Track上，论文参见：[LicenseRec: Knowledge based Open Source License Recommendation for OSS Projects](https://zhcxww.github.io/files/LicenseRec_DEMO.pdf).

快来上传你的项目，在[licenserec.com](https://licenserec.com/)上挑选最佳的开源许可证吧!

## 安装

LicenseRec可以通过两种方式安装：使用Docker或手动。查看[DEPLOY.md](./DEPLOY.md)中的部署说明。

## 知识库
[开源许可证知识库（knowledge_base）](./knowledge_base/)文件夹下，包含了开源许可证兼容性矩阵、条款特征矩阵、兼容性判定方法等资料。包括为机器阅读而建立的文件（即本工具的输入），以及为人类理解而建立的文件（具有更多的解释）。

## 许可证和鸣谢

LicenseRec是根据[木兰公共许可证v2](http://license.coscl.org.cn/MulanPubL-2.0)授权的。详情见[LICENSE](LICENSE)。

LicenseRec依赖于以下开源项目。

* [scancode-tookit](https://github.com/nexB/scancode-toolkit)采用[Apache-2.0](https://opensource.org/licenses/Apache-2.0)授权。（我们增加和修改了一些检测规则。）
* [depend](https://github.com/multilang-depends/depends) 采用[MIT](https://opensource.org/licenses/MIT)授权。


## Introduction

LicenseRec is an open source license recommendation tool that helps developers choose a optimal license for their OSS project.
LicenseRec performs fine-grained license compatibility checks on OSS projects’ code and dependencies, and assists developers to choose the optimal license through an interactive wizard with guidelines of three aspects: personal open source style, business pattern, and community development.

The tool is available at [licenserec.com](https://licenserec.com/) and the demonstration video is at [video.licenserec.com](https://video.licenserec.com/).The tool has been published in the DEMO Track of ICSE'23, see the paper: [LicenseRec: Knowledge based Open Source License Recommendation for OSS Projects](https://zhcxww.github.io/files/LicenseRec_DEMO.pdf).

Upload your project and pick the best open source license on [licenserec.com](https://licenserec.com/)!

## Installation

LicenseRec can be installed in two ways: using Docker or manually. Check deployment instructions in [DEPLOY.md](./DEPLOY.md).

## Knowledge base
The [knowledge_base](./knowledge_base/) folder contains information on open source license compatibility matrix, term feature matrix, compatibility judgment method, and so on. There are two groups of files: files for machine reading (i.e, input for this tool), and files for human understanding (with more explanation about license compatibility).

## License and Acknowledgements

LicenseRec is licensed under [MulanPubL-2.0](http://license.coscl.org.cn/MulanPubL-2.0). See [LICENSE](LICENSE) for details.

LicenseRec relies on the following open source projects:

* [scancode-tookit](https://github.com/nexB/scancode-toolkit) is licensed under [Apache-2.0](https://opensource.org/licenses/Apache-2.0).(We added and modified some detection rules.)
* [depends](https://github.com/multilang-depends/depends) is licensed under [MIT](https://opensource.org/licenses/MIT).
