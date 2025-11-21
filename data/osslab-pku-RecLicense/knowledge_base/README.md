# 知识库文件介绍
知识库包括两组文件：

1，供人类阅读的文件（具有更好的解释性）: `TermFeatures_63license_cn.xlsx`、`Compatibility_63licenses_cn.xlsx`, 在此目录下。
* [TermFeatures_63license_cn.xlsx](./TermFeatures_63license_cn.xlsx)描述了“基本信息,序言,定义,版权授予,专利授予,商标权限制,限制性,网络部署,修改声明,保留归属,增强归属,明确接受许可,专利终止,违约终止,免责声明,准据法,使用说明,版本兼容,次级许可证,gpl组合兼容"等条款维度的含义，并对比了63个开源许可证在前述条款维度上的差异。
* [Compatibility_63licenses_cn.xlsx](./Compatibility_63licenses_cn.xlsx)是对`compatibility_63.csv`中兼容性结论的数据解释，并对当前官网已有的兼容性实例进行了引用标注，给出相关链接便于查阅。  

2，供机器阅读的文件（直接作为程序输入）：`licenses_terms_63.csv`、`compatibility_63.csv`、`github_license_usage.csv`、`libraries.io_license_usage.csv`，它们都被置于[files for program input](./files%20for%20program%20input/)文件夹下。
* [licenses_terms_63.csv](./files%20used%20for%20program%20input/licenses_terms_63.csv)是将`TermFeatures_63license_cn.xlsx`中的特征表示为数值，便于程序输入。其中，版权授予(copyright)取值为-1、0、1(分别表示公共领域、模糊授予版权、明确授予版权)；限制性(copyleft)取值为 0、1、2、3(分别表示宽松型、文件级弱限制型、库级弱限制型、限制型)；专利授权(patent)取值为-1、0、1(分别表示不授予专利权、无提及、明确授予专利权)；准据法(law)取值为 0、country(分别表示无提及、指定国家法律)；兼容版本(compatible_version)取值为 0、license(分别表示无提及、兼容版本的许可证)；次级许可证(secondary_license)取值为 0、license(分别表示无提及、兼容的次级许可证)；其余维度取值为 0、1(分别表示无提及、明确包含该条款)。  
* [compatibility_63.csv](./files%20used%20for%20program%20input/compatibility_63.csv)是根据`licenses_terms_63.csv`和许可证兼容性判定逻辑(如下图)进行判定，得到的63个开源许可证兼容性列表。判定兼容性的算法见[伪代码](../appendix/compatibility_algorithm.pdf)与[python实现](https://github.com/osslab-pku/OSSLSelection/blob/main/OSSLSelection/scripts/compatibility_63.py)。该文件可直接用作程序输入。          
* [github_license_usage.csv](./files%20used%20for%20program%20input/github_license_usage.csv)、[libraries.io_license_usage.csv](./files%20used%20for%20program%20input/libraries.io_license_usage.csv)是根据GitHub和Libraries.io上许可证使用情况的统计数据。   


![image](https://github.com/osslab-pku/RecLicense/blob/master/appendix/check_compatibility_cn.png)
    
## 注：兼容性定义

1. A次级兼容B：修改或组合开源许可证A授权的作品，所产生的衍生作品整体可采用许可证B授权，且衍生作品中所有部分(包括原许可证A授权部分)都遵循许可证B的约束。例如，Apache-2.0授权的软件经过修改或组合，可以使用GPL-3.0 重新授权并分发。
2. A组合兼容B：修改或组合许可证A授权的作品，所产生的衍生软件整体可采用许可证B授权，而衍生作品中原许可证A授权部分仍然遵循许可证A的约束。组合软件中可能包含多个不同的开源许可证，并各自约束其授权部分，例如调用了LGPL-2.1 授权的库的软件，可以使用 Apache-2.0整体授权并分发，只要满足其调用的库仍然遵循LGPL-2.1的约束。

如图所示为种兼容性的示意图：

![image](https://github.com/osslab-pku/RecLicense/blob/master/appendix/CompatibilityExample.png)

# Introduction
We provide two groups of files for the knowledge base used in this tool. 

1, files for human understanding: `TermFeatures_63license_en.xlsx`, `Compatibility_63licenses_en.xlsx`, which contain more information about license compatibility for human understanding, located in this folder.
* [TermFeatures_63license_en.xlsx](./TermFeatures_63license_en.xlsx) describes the meanings of "basic information, preamble	definition, Copyright Grant, Petent Grant, Restriction of Trademark Rights, Copyleft, Network deployment, Modification Statement, Attribution Retention, Attribution Enhancement,	Express Acceptance, Patent Termination, Violation Termination,	Disclaimers, Proper Law, Instruction, Compatible Version,Secondary License,combinative compatibility of GPL" and compares the differences of these terms among 63 open source licenses.
*  [Compatibility_63licenses_en.xlsx](./Compatibility_63licenses_en.xlsx) explains the compatibility conclusions in the `compatibility_63.csv` with reference to the compatibility examples of licenses currently available on official websites, and provides related links for easy access.

2, files for machine reading (input for this tool): `licenses_terms_63.csv`, `compatibility_63.csv`, `github_license_usage.csv`, `libraries.io_license_usage.csv`. They are located in the [files for program input](./files%20for%20program%20input/) folder.

*  [licenses_terms_63.csv](./files%20used%20for%20program%20input/licenses_terms_63.csv) represents the features from "TermFeatures_63license_en.xlsx" in numerical values, where the values for copyright are -1, 0, and 1 (representing public domain, ambiguous copyright, and explicit copyright). The values for copyleft are 0, 1, 2, and 3 (representing permissive, file-level copyleft, library-level copyleft, and strict copyleft, respectively). The values for patent are -1, 0, and 1 (representing no patent grant, no mention, and explicit patent grant). The values for proper law are 0 and country (representing no mention and designated country jurisdiction). The values for compatible version and secondary license are 0 and license (representing no mention and compatible version license or compatible secondary license). This file can be used as program inputs.
*  [compatibility_63.csv](./files%20used%20for%20program%20input/compatibility_63.csv) is a list of the compatibility conclusions of 63 open source licenses based on the compatibility judgment logic of license terms indicated in the above `licenses_terms_63.csv`. The algorithm used for determining compatibility is shown in [pseudocode](../appendix/compatibility_algorithm.pdf) and [Python implementation](https://github.com/osslab-pku/RecLicense/blob/master/appendix/compatibility_63.py). This file can be used as program inputs.
*   [github_license_usage.csv](./files%20used%20for%20program%20input/github_license_usage.csv) and [libraries.io_license_usage.csv](./files%20used%20for%20program%20input/libraries.io_license_usage.csv) are statistics of license usage from GitHub and Libraries.io.

![image](https://github.com/osslab-pku/RecLicense/blob/master/appendix/check_compatibility.png)


## Note: Definition of Compatibility

1. Secondary Compatibility : When a work licensed under Open Source License A is modified or combined, the resulting derivative work as a whole can be re-licensed under License B, provided that all parts of the derivative work (including the parts originally under License A) comply with the constraints of License B. For example, software licensed under Apache-2.0 can be modified or combined and then re-licensed and distributed under GPL-3.0.
2. Combinative Compatibility: When a work licensed under License A is modified or combined, the resulting derivative software as a whole can be re-licensed under License B, while the portions originally under License A still adhere to License A’s constraints. The combined software may include multiple different open source licenses, each of which governs its respective parts. For instance, software that calls a library licensed under LGPL-2.1 can be re-licensed and distributed under Apache-2.0 as a whole, as long as the called library still adheres to the constraints of LGPL-2.1.

As shown in the figure, the diagram illustrates the types of compatibility: 

![image](https://github.com/osslab-pku/RecLicense/blob/master/appendix/CompatibilityExample.png)
