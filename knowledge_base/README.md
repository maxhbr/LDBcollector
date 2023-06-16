# 文件介绍
本工具用到的知识库包括：“licenses_terms_63.csv”、“compatibility_63.csv”、“github_license_usage.csv”、“libraries.io_license_usage.csv”, 它们都被置于[files for program input](./files%20used%20for%20program%20input/)文件夹下，可直接作为程序输入。

1. [TermFeatures_63license_cn.xlsx](./TermFeatures_63license_cn.xlsx)描述了“基本信息,序言,定义,版权授予,专利授予,商标权限制,限制性,网络部署,修改声明,保留归属,增强归属,明确接受许可,专利终止,违约终止,免责声明,准据法,使用说明,版本兼容,次级许可证,gpl组合兼容"等条款维度的含义，并对比了63个开源许可证在前述条款维度上的差异。   
2. [licenses_terms_63.csv](./files%20used%20for%20program%20input/licenses_terms_63.csv)是将“63个开源许可证条款特征.xlsx”中的特征表示为数值，其中，版权授予(copyright)取值为-1、0、1(分别表示公共领域、模糊授予版权、明确授予版权)；限制性(copyleft)取值为 0、1、2、3(分别表示宽松型、文件级弱限制型、库级弱限制型、限制型)；专利授权(patent)取值为-1、0、1(分别表示不授予专利权、无提及、明确授予专利权)；准据法(law)取值为 0、country(分别表示无提及、指定国家法律)；兼容版本(compatible_version)取值为 0、license(分别表示无提及、兼容版本的许可证)；次级许可证(secondary_license)取值为 0、license(分别表示无提及、兼容的次级许可证)；其余维度取值为 0、1(分别表示无提及、明确包含该条款)   
3. [compatibility_63.csv](./files%20used%20for%20program%20input/compatibility_63.csv)是根据“licenses_terms_63.csv”和许可证兼容性判定逻辑(如下图)进行判定，得到的63个开源许可证兼容性列表。判定兼容性的算法见[伪代码](../appendix/compatibility_algorithm.pdf)与[python实现](https://github.com/osslab-pku/OSSLSelection/blob/main/OSSLSelection/scripts/compatibility_63.py)。          
4. [Compatibility_63licenses_cn.xlsx](./Compatibility_63licenses_cn.xlsx)是对[compatibility_63.csv](./files%20used%20for%20program%20input/compatibility_63.csv)中兼容性结论的数据解释，并对当前官网已有的兼容性实例进行了引用标注，给出相关链接便于查阅。  
5. [github_license_usage.csv](./files%20used%20for%20program%20input/github_license_usage.csv)、[libraries.io_license_usage.csv](./files%20used%20for%20program%20input/libraries.io_license_usage.csv)是根据GitHub和Libraries.io上许可证使用情况的统计数据。   


![image](https://github.com/osslab-pku/OSSLSelection/assets/24621557/b37a4793-9333-418f-b8cb-dc5b80505367)
    


# Introduction
The knowledge base used in this tool includes "licenses_terms_63.csv", "compatibility_63.csv", "github_license_usage.csv", "libraries.io_license_usage.csv". They are all placed in the [files for program input](./files%20used%20for%20program%20input/) folder and can be used directly as program inputs.


1. [TermFeatures_63license_en.xlsx](./TermFeatures_63license_en.xlsx) describes the meanings of "basic information, preamble	definition, Copyright Grant, Petent Grant, Restriction of Trademark Rights, Copyleft, Network deployment, Modification Statement, Attribution Retention, Attribution Enhancement,	Express Acceptance, Patent Termination, Violation Termination,	Disclaimers, Proper Law, Instruction, Compatible Version,Secondary License,combinative compatibility of GPL" and compares the differences of these terms among 63 open source licenses.
2. [licenses_terms_63.csv](./files%20used%20for%20program%20input/licenses_terms_63.csv) represents the features from "TermFeatures_63license_en.xlsx" in numerical values, where the values for copyright are -1, 0, and 1 (representing public domain, ambiguous copyright, and explicit copyright). The values for copyleft are 0, 1, 2, and 3 (representing permissive, file-level copyleft, library-level copyleft, and strict copyleft, respectively). The values for patent are -1, 0, and 1 (representing no patent grant, no mention, and explicit patent grant). The values for proper law are 0 and country (representing no mention and designated country jurisdiction). The values for compatible version and secondary license are 0 and license (representing no mention and compatible version license or compatible secondary license).

3. [compatibility_63.csv](./files%20used%20for%20program%20input/compatibility_63.csv) is a list of the compatibility conclusions of 63 open source licenses based on the compatibility judgment logic of license terms indicated in the above "licenses_terms_63.csv". The algorithm used for determining compatibility is shown in [pseudocode](../appendix/compatibility_algorithm.pdf) and [Python implementation](https://github.com/osslab-pku/OSSLSelection/blob/main/OSSLSelection/scripts/compatibility_63.py).

4. [Compatibility_63licenses_en.xlsx](./Compatibility_63licenses_en.xlsx) explains the compatibility conclusions in the "compatibility_63.csv" with reference to the compatibility examples of licenses currently available on official websites, and provides related links for easy access.

5. [github_license_usage.csv](./files%20used%20for%20program%20input/github_license_usage.csv) and [libraries.io_license_usage.csv](./files%20used%20for%20program%20input/libraries.io_license_usage.csv) are statistics of license usage from GitHub and Libraries.io.

![image](https://github.com/osslab-pku/OSSLSelection/assets/24621557/b37a4793-9333-418f-b8cb-dc5b80505367)
    
