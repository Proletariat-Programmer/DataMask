# 项目设计

## 模块拆解

| 模块名称 | 模块功能           |
| -------- | ------------------ |
| 登陆     | 进行登陆验证       |
| 上传     | 文件上传与表单填写 |
| 历史记录 | 提供历史记录查询   |
| 分析展示 | 分析后的结果界面   |

## 模块详情

### 登陆

| 功能 | 解释                 | URL      |
| ---- | -------------------- | -------- |
| 登陆 | 用户名/手机号 + 密码 | login    |
| 登出 | nil                  | logout   |
| 注册 | 用户名/手机号 + 密码 | register |

### 上传

| 功能          | 解释            | URL    |
| ------------- | --------------- | ------ |
| 上传文件+填表 | file + 表单内容 | upload |

### 历史记录 & 主界面

| 功能     | 解释             | URL          |
| -------- | ---------------- | ------------ |
| 历史list | 返回历史上传list | history_list |

### 分析展示

| 功能               | 解释            | URL             |
| ------------------ | --------------- | --------------- |
| 单个上传的分析结果 | 通过load_id定位 | Analysis_result |

## 开发计划

后端选用 flask

用户登陆认证采用 flask-login

数据库交互认证采用 flask-sqlalchemy

门槛低，大家能看懂

| URL                                                  | 调研结果                |
| ---------------------------------------------------- | ----------------------- |
| https://github.com/shekhargulati/flask-login-example | 纯登陆，调用flask-Login |
| https://github.com/tolgahanuzun/Flask-Login-Example  | 用来登陆ins的           |

环境配置

```shell
# 激活conda环境。 pip安装依赖包
conda activate pyclone
pip3 install flask
pip3 install flask-login
pip3 install flask-sqlalchemy
pip3 install PyMySQL
```

### 数据库设计

需要登陆模块 处理登陆相关逻辑

分析结果模块 用来查看上传文件状态(3个)

用户表

```
CREATE` `TABLE` ``user` (
 ```id` ``int``(11) unsigned ``NOT` `NULL` `AUTO_INCREMENT COMMENT ``'id'``,
 ```user_name` ``varchar``(30) ``NOT` `NULL` `DEFAULT` `''` `COMMENT ``'用户名称'``,
 ```password` ``varchar``(100) ``NOT` `NULL` `DEFAULT` `''` `COMMENT ``'用户密码'``,
 ```phone` ``varchar``(100) ``NOT` `NULL` `DEFAULT` `''` `COMMENT ``'用户手机号'``,
 ```ctime` datetime ``NOT` `NULL` `DEFAULT` `CURRENT_TIMESTAMP` `COMMENT ``'账号的创建时间'``,
 ```mtime` datetime ``NOT` `NULL` `DEFAULT` `CURRENT_TIMESTAMP` `ON` `UPDATE` `CURRENT_TIMESTAMP` `COMMENT ``'最后更新时间'``,
 ``PRIMARY` `KEY` `(`id`) USING BTREE,
 ``KEY` ``ix_ctime` (`ctime`) USING BTREE,
 ``KEY` ``ix_mtime` (`mtime`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 ``DEFAULT` `CHARSET = utf8 COMMENT = ``'用户配置表'``;
```

分析结果表

```
CREATE` `TABLE` ``result` (
 ```id` ``int``(11) unsigned ``NOT` `NULL` `AUTO_INCREMENT COMMENT ``'id'``,
 ```user_name` ``varchar``(30) ``NOT` `NULL` `DEFAULT` `''` `COMMENT ``'用户名称'``,
 ```password` ``varchar``(100) ``NOT` `NULL` `DEFAULT` `''` `COMMENT ``'用户密码'``,
 ```phone` ``varchar``(100) ``NOT` `NULL` `DEFAULT` `''` `COMMENT ``'用户手机号'``,
 ```ctime` datetime ``NOT` `NULL` `DEFAULT` `CURRENT_TIMESTAMP` `COMMENT ``'账号的创建时间'``,
 ```mtime` datetime ``NOT` `NULL` `DEFAULT` `CURRENT_TIMESTAMP` `ON` `UPDATE` `CURRENT_TIMESTAMP` `COMMENT ``'最后更新时间'``,
 ``PRIMARY` `KEY` `(`id`) USING BTREE,
 ``KEY` ``ix_ctime` (`ctime`) USING BTREE,
 ``KEY` ``ix_mtime` (`mtime`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 ``DEFAULT` `CHARSET = utf8 COMMENT = ``'用户配置表'``;
```

#### Mysql流程

##### ~~Py与数据库的连接~~

Python 与 mysql连接 https://github.com/PyMySQL/PyMySQL

##### Mysql全配置流程

```shell
# -------       docker安装后 快速部署本地mysql环境      ------- #

# docker 搜索mysql
docker search mysql
# docker 拉取最新版本
docker pull mysql:latest
# docker 查看本地镜像
docker images
# 初次运行 mysql
docker run -itd --name mysql2 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql
# 或从已停止的容器重新启动
docker start xxx(docker ps -a 显示的对应号码)
# 进入容器内部命令行
docker exec -it mysql2 bash
# 在虚拟机中进入mysql
mysql -uroot -p123456
# 虚拟机中创建数据库
CREATE SCHEMA test;
# 退出
exit;
# 直接运行flask-sqlalchemy调研处shell指令即可完成mysql全部环境部署
```

##### flask-sqlalchemy调研

在flask中使用SQLAlchemy数据库框架对数据库驱动进一步封装，进一步简化命令。 因此SQLAlchemy不是数据库，而是对数据库进行操作的一种框架。

filter模糊查询，返回名字结尾字符为g的所有数据

```shell
# 运行在部署完成mysql后，完成数据库部分全部部署
python3 database_init.py
```

### 接入分析系统

方案 : subprocess直接开子进程调用，直接从后台调用pyclone，想想还是很美好的

所以分析系统接入使用

pyclone环境构建。https://github.com/Roth-Lab/pyclone

```shell
# install PyClone using bioconda.
conda install pyclone -c bioconda -c conda-forge
# create a separate conda environment for PyClone
conda create -n pyclone -c bioconda -c conda-forge pyclone
# activated using the following command.
conda activate pyclone
# check that PyClone was installed
PyClone --help
```

直接在服务中起指令调研 run 和 popen

`subprocess.run`在 Python3.5添加，作为对`subprocess.Popen`的简化

当只想执行一个命令并等待它完成，但不想同时执行任何其他操作时。对于其他情况，仍然需要使用subprocess.Popen

主要的区别是subprocess.run执行一个命令并等待它完成，而使用subprocess.Popen您可以在进程完成时继续执行您的工作，然后只需重复调用subprocess.communicate就可以向进程传递和接收数据。

注意，subprocess.run实际上所做的是为您调用Popen和communicate，因此您不需要进行循环来传递/接收数据，也不需要等待进程完成

所以可以使用run方法来完成这次任务

```shell
# 以前用法
subprocess.Popen("aireplay-ng -0 15 -a " + BS +" wlan0mon", shell = True, stdout = subprocess.PIPE)
# 用法1 直接生成结果
subprocess.run(" PyClone build_mutations_file --in_flies xxx.tsv --out_file yyy.yaml")
# 用法2 运行一个分析流程
subprocess.run("PyClone run_analysis_pipeline --in_files xxx.tsv --working_dir test_dir")
```

- `--in_files`: A space delimited set of tsv files formatted as specified in the input format section.
- `--working_dir`: A directory where the pipeline will run and output results.

输入文件选用 up_loads/x/yy.tsv

输出路径选择 analysis_result/x/yy/.*

运行成功后修改数据库，可以合理测试

调用方法大致为

```python
import subprocess
A = 0
try:
      A = subprocess.run(["ls", "-l"]).returncode
except:
    A = 1
 if A != 0:
    # 出现异常情况
    print("出现异常情况")
         return

# 正常情况
print("分析成功结束")
```

### 数据处理流程

输入文件通过文件上传功能上传至服务器。

服务器将新上传的输入文件加入处理队列

可以在/historylist路径中看到所有上传的文件的处理状态

| 状态名 | 解释                                                 |
| ------ | ---------------------------------------------------- |
| 已完成 | 已经分析完成，可以进行结果展示                       |
| 处理中 | 当前分析文件，正在流程处理中 (考虑展示百分比进度条?) |
| 等待中 | 等待处理文件队列...                                  |

#### 数据处理具体节点与详细流程

upload上传后，检测后缀名&解析文件内容检测，进入upload_list队列，分析完成后，将结果放入一个特定的路径中

就像analysis_result（文档后续简称ar）

然后在 ar/X/...创建对应文件夹并存入内容

最后在history_list展示结果时，对每个文件，检测ar/X/...中是否存在对应文件夹，若存在则返回已完成，若不存在，但其位于upload_list首位，则返回处理中，否则其余情况返回等待中

## 分析结果展示

传入 upfile_id 返回 几个展示结果的url

目前计划以html a标签来实现

```html
<a target='_black'  href='http://mczaiyun.top/ht/4.pdf'>预览PDF文件</a>
```

## 操作流程

```
'''
# TODO 是否有优化的空间
目前共十步
1 进入网站
2 未登陆强制跳转到登陆界面
3 注册
4 登陆
5 登陆至主界面
6 点击"新建"，填写表单并上传文件
7 点击提交后，跳转到历史上传页面
8 查看文件处理状态
9 等待完成后,点击文件图标
10 展示此文件处理结果
'''
```

上传文件状态逻辑优化

数据库新增状态相关操作

以上两个判断逻辑思考

当前逻辑

1 文件上传后，文件存储到对应位置

2 将此文件加到处理队列

3 使用多线程监控处理队列

4 将处理队列 leftpop 将新出来的这个目标放到处理函数位置

优化逻辑

1 上传并存储到对应位置后，在数据库中添加记录

2 并将此文件的 file_id 推到任务队列中

3 监控任务队列是否为空

4 不为空时，leftpop出来下一个等待被处理的 file_id

5 通过mysql查询对应信息，送入处理函数

优化逻辑的优势

可以通过数据库随时查询内容，第一版设计有一个问题是没有地方对所有数据进行集中化处理

## 技术实现调研

#### 旧版本flask.ext.login

https://stackoverflow.com/questions/21701174/importerror-no-module-named-flask-ext-login

#### python上传文件

官方推荐 http://docs.jinkan.org/docs/flask/patterns/fileuploads.html

一个简单例子=。= https://www.cnblogs.com/wongbingming/p/6802660.html

#### flask_login 获取当前登陆用户

Flask-login 一个比较全的小文 http://www.ityouknow.com/python/2019/11/13/python-web-flask-login-057.html

```
from flask import render_template, url_for
from flask_login import current_user, login_required
# ...

# 获取
@app.route('/')  # 首页
@login_required  # 需要登录才能访问
def index():
    return render_template('index.html', username=current_user.username)
```

#### 按照用户分割上传空间

设用户id为X,用户上传路径为 uploads/X/...具体文件

#### 检测路径存在|创建新文件夹

检测 https://www.runoob.com/w3cnote/python-check-whether-a-file-exists.html

检测创建 https://blog.51cto.com/tenderrain/1590191

也是检测创建 http://www.chenxm.cc/article/1116.html

#### Python队列

https://www.cnblogs.com/huangxm/p/5215583.html

#### Flask对协程的支持

感觉直接用官方例子就行，python协程太久不用了...但是！还是要用协程！

（为凸显重剑无锋快糙猛的方法论，转头投向多线程的怀抱）

```
import asyncio


async def main():
    print('Hello ...')
    await asyncio.sleep(1)
    print('... World!')

    
# Python 3.7+
asyncio.run(main())
```

https://docs.python.org/3/library/asyncio.html

#### Docker不同容器间通信

三种方法(推荐第三种)

1 虚拟ip互访

2 link 在运行容器的时候加上参数link

--link：参数中第一个centos-1是**容器名**，第二个centos-1是定义的**容器别名**（使用别名访问容器），为了方便使用，一般别名默认容器名。

3 创建bridge网络

（1） 安装好docker后，运行如下命令创建bridge网络：docker network create testnet

使用 docker network ls 查询到新创建的bridge testnet。

（2）运行容器连接到testnet网络。

使用方法：docker run -it --name <容器名> ---network --network-alias <网络别名> <镜像名>

```
[root@CentOS ~]# docker run -it --name centos-1 --network testnet --network-alias centos-1 docker.io/centos:latest
[root@CentOS ~]# docker run -it --name centos-2 --network testnet --network-alias centos-2 docker.io/centos:latest
```

（3）从一个容器ping另外一个容器，测试之

（4）若访问容器中服务，可以使用这用方式访问 <网络别名>：<服务端口号>

推荐使用这种方法，自定义网络，因为使用的是网络别名，可以不用顾虑ip是否变动，只要连接到docker内部bright网络即可互访。bridge也可以建立多个，隔离在不同的网段

network模式 https://blog.csdn.net/beeworkshop/article/details/106017711

Docker容器互访三种方式 https://www.cnblogs.com/shenh/p/9714547.html

测试结果可以ping通过

```
(base) root@077ff6879f06:/# ping mysql2
PING mysql2 (192.168.176.2) 56(84) bytes of data.
64 bytes from mysql2.bs-test (192.168.176.2): icmp_seq=1 ttl=64 time=0.180 ms
64 bytes from mysql2.bs-test (192.168.176.2): icmp_seq=2 ttl=64 time=0.192 ms
^C
--- mysql2 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 4ms
rtt min/avg/max/mdev = 0.180/0.186/0.192/0.006 ms
```

#### pymysql报错缺少依赖

cryptography is required for sha256_password or caching_sha2_password

```shell
pip3 install cryptography
```

#### 脱敏

脱敏 (姓名，年龄)

#### 结果展示方法调研

9个图片都展示，tables展示cluster

loci提供下载

#### redis缓存调用

所有的行为-> 存储到缓存 -> 缓存再写入到数据库

redis（Mysql）

缓存 

### 二期规划

二期可拓展方向(现仅为脑洞)

| 标题                | 内容                                |
| ------------------- | ----------------------------------- |
| history历史上传文件 | 基于日期强规则 与name的模糊匹配技术 |
| 实名验证            | 功能简单，后置                      |
| 发送邮件            | 发现flask_mail框架可以实现          |

### 唧唧歪歪

上传文件后，有一个开始分析的按钮..?然后再开始分析

| 状态名 | 解释                             |
| ------ | -------------------------------- |
| 未分析 | 上传后，尚未点击 "开始分析"      |
| 准备中 | 建立分析然后开始排队等待分析处理 |

###### TODOList

#### 高

结果展示

#### 普通

脱敏

#### 低

加redis缓存

------

从前端直接访问图片资源

因为实时分析不会立刻出结果，所以先把用户送到主界面

主界面可以选择 上传文件 ｜ 历史记录

pb。json
