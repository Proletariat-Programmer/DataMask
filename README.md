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

检查安装 PyClone --help

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

#### 数据分析方法&结果展示

在一开始加载输入文件名和输出路径名

##### 数据分析

###### cli入口

加载各个模块(解析参数->进行分析->分析管道流->建立突变文件->绘制clusters->绘制loci->建表)

_setup_setup_analysis_parser设置分析：首先确定输入文件，工作路径，肿瘤列表，样本数据，临时配置文件，浓度，迭代次数内容，最后运行parser.set_defaults(func=run.setup_analysis)函数进行文件设置

_setup_run_analysis_parser分析函数：加载参数,设随机种子，最后运行parser.set_defaults(func=run.run_analysis)函数处理

_setup_analysis_pipeline_parser分析管道流：加载参数，增加_process参数，设随机种子，读取输出格式(默认pdf，还可以svg)，设最大clusters，mesh大小，最小clusters。最后运行parser.set_defaults(func=run.run_analysis_pipeline)

_setup_build_prior_parser建立突变文件：确定输入输出文件，先验参数parser.set_defaults(func=run.build_mutations_file)

_setup_build_table_parser建表：加载outfile，table_type，cluster最大值，mesh大小，post处理流程，parser.set_defaults(func=run.build_table)

---

###### run函数解析

**_setup_analysis**

创建工作路径，yaml文件，对infile的每种参数进行拼接，创建突变文件。最后将参数都写入到config.yaml文件中

**run_analysis** 

加载随机种子，加载配置文件，若配置中'concentration浓度'.'先验'存在则加载，加载num_iters，加载density密度

判断浓度是否为二项式或贝塔二项式，是则加载对应函数，否则raise Exception报错

**run_analysis_pipeline**

加载配置，调用_setup_analysis，加载tables路径且创建文件，对于['cluster', 'loci']进行绘图，

绘图明细

```python
    plots = [
        ('cluster', 'density'),
        ('cluster', 'parallel_coordinates'),
        ('cluster', 'scatter'),
        ('loci', 'density'),
        ('loci', 'parallel_coordinates'),
        ('loci', 'scatter'),
        ('loci', 'similarity_matrix'),
        ('loci', 'vaf_parallel_coordinates'),
        ('loci', 'vaf_scatter')
    ]
```

**build_table**

判断表类型['cluster','loci','lod_style']执行格式转化，变为tsv

df.to_csv(out_file, index=False, sep='\t')

**build_mutations_file**

读取csv文件reader = csv.DictReader(open(in_file), delimiter='\t')

将读取到的ref_counts...major_cn这些参数都提取出来

创建对应路径并打开输出文件文件

yaml.dump(config, fh, Dumper=Dumper)打印文件

最后关闭文件

-----

###### 文件作用一览

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

#### 数据集样例解读

数据集有标签(AB,BB)

125行9列无缺省字段

ref_counts variant_freq PEARSON相关有0.95

minor_cn major_cn 相关系数-1

#### 调研机器学习算法实现

pass 待完成

#### 主体代码逻辑结构图

![s](picture/s.png)

## 其他操作指引

#### 数据聚类

**SciPy 聚类包**。  from scipy.cluster.vq import *

```python
from scipy.cluster.vq import *
from numpy.random import randn
from numpy import array
from numpy import vstack

class1 = 1.5 * randn(100,2)
class2 = randn(100,2) + array([5,5])

features = vstack((class1,class2))
# 上面的代码生成两类二维正态分布数据。用 k=2 对这些数据进行聚类：
centroids,variance = kmeans(features,2)
'''
由于 SciPy 中实现的 K-means 会计算若干次（默认为 20 次），并为我们选择方差最 小的结果，所以这里返回的方差并不是我们真正需要的。现在，你可以用 SciPy 包 中的矢量量化函数对每个数据点进行归类：
'''
code,distance = vq(features,centroids)
# 通过上面得到的 code，我们可以检查是否有归类错误。为了将其可视化，我们可以 画出这些数据点及最终的聚类中心

figure() ndx = where(code==0)[0]

plot(features[ndx,0],features[ndx,1],'*') ndx = where(code==1)[0] plot(features[ndx,0],features[ndx,1],'r.')

plot(centroids[:,0],centroids[:,1],'go') axis('off')

show()
```

