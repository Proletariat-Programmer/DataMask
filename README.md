# DataMask
数据隐匿保护系统

## 介绍

该系统主要分为两部分：数据安全处理和数据隐私发布

| 项目名称                         | 实现重点                               |
| -------------------------------- | -------------------------------------- |
| 医疗数据安全处理系统的设计与实现 | 侧重的是数据的处理和分析，及前台的展示 |
| 医疗数据隐私发布系统的设计与实现 | 侧重的是医疗数据的隐私保护与系统设计   |

## 资料

| 名称           | 地址                                                         |
| -------------- | ------------------------------------------------------------ |
| PyClone-paper  | https://www.nature.com/articles/nmeth.2883                   |
| PyClone-代码   | https://github.com/Roth-Lab/pyclone                          |
| SciClone-paper | https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003665 |
| SciClone-代码  | https://github.com/genome/sciclone                           |

## PyCLone

#### 代码运行

安装conda

安装bioconda。 http://bioconda.github.io/user/install.html

创建环境 conda create -n pyclone -c bioconda -c conda-forge pyclone

激活程序 conda activate pyclone

测试1 直接生成结果 PyClone build_mutations_file --in_flies xxx.tsv --out_file yyy.yaml

测试2 PyClone run_analysis_pipeline --in_files xxx.tsv --working_dir test_dir

代码至此全部成功运行且结果正确

#### 输入格式

大多数用户将通过创建一组制表符分隔（tsv）输入文件来使用PyClone，每个文件来自癌症的每个样本。此文件的必填列如下。

- variant_id：突变的唯一标识符。跨数据集应该是相同的。
- ref_counts：与参考等位基因匹配的基因座重叠的读段数。
- var_counts：与匹配变异等位基因的基因座重叠的读段数。
- normal_cn：非恶性细胞中基因座的拷贝数。除男性的性染色体外，通常应为2。
- minor_cn：恶性细胞中次要等位基因的拷贝数。该值必须小于major_cn列中的值。
- major_cn：恶性细胞中主要等位基因的拷贝数。该值应大于等于minor_cn列中的值且大于0。

任何其他列都将被忽略。示例文件被发现[这里](https://github.com/Roth-Lab/pyclone/tree/master/examples/mixing/tsv)从原来的PyClone本文所采用的混合数据集。

#### 数据分析方法&结果展示

在一开始加载输入文件名和输出路径名

##### 数据分析

cli处理逻辑

读取餐素

加载各个模块(解析参数->进行分析->分析管道流->建立突变文件->绘制clusters->绘制loci->建表)

最终args.func(args)运行功能

---



_setup_run_analysis_parser分析函数：加载参数,设随机种子，最后运行parser.set_defaults(func=run.run_analysis)函数处理



_setup_analysis_pipeline_parser分析管道流：加载参数，增加_process参数，设随机种子，读取输出格式(默认pdf，还可以svg)，设最大clusters，mesh大小，最小clusters。

最后运行parser.set_defaults(func=run.run_analysis_pipeline)

---



| cli                     | 程序入口                           |
| ----------------------- | ---------------------------------- |
| sampler取样             | 对详细数据,密度分别取样            |
| binomial二项式          | 提供二项式分析                     |
| beta_binmmial贝塔二项式 | 提供贝塔二项式分析                 |
| math_uils               | 为二项式提供方法支持               |
| multi_sample            | 允许在PyDP框架中分析多个样本的功能 |
| run                     | 承接cli具体功能实现                |
| ...还有一些功能性模块   |                                    |

##### 输出部分

###### 图像

输出集中在post_access中

分为polt文件夹 clusters集群 loci基因

后两者会被polt文件夹中的代码调用，最终生成图像

