# 文件介绍
本工具用到的知识库包括：“licenses_terms_63.csv”、“compatibility_63.csv”、“github_license_usage.csv”、“libraries.io_license_usage.csv”、“license_readability.csv”、“license_recommended.csv”,其中：
1. “63个开源许可证条款特征.xlsx”描述了“基本信息,序言,定义,版权授予,专利授予,商标权限制,限制性,网络部署,修改声明,保留归属,增强归属,明确接受许可,专利终止,违约终止,免责声明,准据法,使用说明,版本兼容,次级许可证,gpl组合兼容"等条款维度的含义，并对比了63个开源许可证在前述条款维度上的差异。   
2. “licenses_terms_63.csv”是将“63个开源许可证条款特征.xlsx”中的特征表示为数值，其中，版权授予(copyright)取值为-1、0、1(分别表示公共领域、模糊授予版权、明确授予版权)；限制性(copyleft)取值为 0、1、2、3(分别表示宽松型、文件级弱限制型、库级弱限制型、限制型)；专利授权(patent)取值为-1、0、1(分别表示不授予专利权、无提及、明确授予专利权)；准据法(law)取值为 0、country(分别表示无提及、指定国家法律)；兼容版本(compatible_version)取值为 0、license(分别表示无提及、兼容版本的许可证)；次级许可证(secondary_license)取值为 0、license(分别表示无提及、兼容的次级许可证)；其余维度取值为 0、1(分别表示无提及、明确包含该条款)   
3. “compatibility_63.csv”是根据“licenses_terms_63.csv”和许可证兼容性判定逻辑(如下图)进行判定，得到的63个开源许可证兼容性列表。判定兼容性的代码实现见（https://github.com/osslab-pku/OSSLSelection/blob/main/OSSLSelection/scripts/compatibility_63.py）。          
4. “63个开源许可证兼容性列表.xlsx”是对“compatibility_63.csv”中兼容性结论的数据解释，并对当前官网已有的兼容性实例进行了引用标注，给出相关链接便于查阅。  
5. “github_license_usage.csv”、“libraries.io_license_usage.csv”是根据GitHub和Libraries.io上许可证使用情况的统计数据。   
6. “license_recommended.csv”是根据“github_license_usage.csv”、“libraries.io_license_usage.csv”的许可证使用情况，构建的用于本工具的推荐许可证列表。   
7. “license_readability.csv”是对“license_recommended.csv”中的许可证，计算其文本可读性。计算文本可读性的代码实现见（https://github.com/osslab-pku/OSSLSelection/blob/main/OSSLSelection/scripts/license_readability.py）。    

![image](https://github.com/osslab-pku/OSSLSelection/assets/24621557/b37a4793-9333-418f-b8cb-dc5b80505367)
    
