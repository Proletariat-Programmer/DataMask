# 项目设计

## 项目模块拆分

| 模块名称 | 模块功能           |
| -------- | ------------------ |
| 登陆     | 进行登陆验证       |
| 上传     | 文件上传与表单填写 |
| 历史记录 | 提供历史记录查询   |
| 分析展示 | 分析后的结果界面   |

## 模块接口与功能详细描述

### 登陆模块

（注册 - 姓名 + 手机号 + 密码）

GET user_init

（登陆 - 姓名\手机号 + 密码）



## 开发计划

后端 选 Python -  flask

原因：门槛低，大家能看懂。带来的结果是=。=我自己的毕设处于代码复用的崇高懒惰目的估计也用python=。=

| URL                                                  | 调研结果                |
| ---------------------------------------------------- | ----------------------- |
| https://github.com/shekhargulati/flask-login-example | 纯登陆，调用flask-Login |
| https://github.com/tolgahanuzun/Flask-Login-Example  | 用来登陆ins的           |

问题解决

https://stackoverflow.com/questions/21701174/importerror-no-module-named-flask-ext-login

安装依赖

```shell
pip3 install flask
pip3 install flask-login
```

简单规划=。=抓紧写

### 登陆

| 路径       | 功能                           |
| ---------- | ------------------------------ |
| /          | hello.html用于测试服务功能开启 |
| /login     | 登陆看板login.html             |
| /register  | 注册界面                       |
| /logout    | 登出logout.html                |
| /dashboard | 登陆后主界面 (尚未测试)        |

### 文件上传 + 表单填写

| 路径    | 功能                                            |
| ------- | ----------------------------------------------- |
| /upload | 选择上传文件并填写表单，事后返回dashboard主界面 |

### 历史记录

| 路径         | 功能                                                     |
| ------------ | -------------------------------------------------------- |
| /historylist | 可以查看历史上传的文件(在这里可以看到历史文件的处理进度) |

历史记录

遍历upload/X/...下所有文件，然后将文件名返回

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



## 操作流程

```python
'''
# TODO 晚上沟通一下是否需要这些步骤，是否有优化的空间
目前共十步
1 进入网站
2 强制跳转到登陆界面
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

### 技术实现调研

#### python上传文件

官方推荐  http://docs.jinkan.org/docs/flask/patterns/fileuploads.html

一个简单例子=。= https://www.cnblogs.com/wongbingming/p/6802660.html

#### flask_login 获取当前登陆用户

Flask-login 一个比较全的小文 http://www.ityouknow.com/python/2019/11/13/python-web-flask-login-057.html

```python
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

```python
import asyncio

async def main():
    print('Hello ...')
    await asyncio.sleep(1)
    print('... World!')

# Python 3.7+
asyncio.run(main())
```

https://docs.python.org/3/library/asyncio.html

### 唧唧歪歪

可以考虑上传文件后，有一个开始分析的按钮..?然后再开始分析

| 状态名 | 解释                             |
| ------ | -------------------------------- |
| 未分析 | 上传后，尚未点击 "开始分析"      |
| 准备中 | 建立分析然后开始排队等待分析处理 |

### 







### TODO

register路径适配

几个url

从前端直接访问图片资源



因为实时分析不会立刻出结果，所以先把用户送到主界面

主界面可以选择       上传文件 ｜ 历史记录  



pb。json 


