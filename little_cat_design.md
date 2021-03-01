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

原因：门槛低，都能看懂。

带来的结果是=。=我自己的毕设处于代码复用的崇高懒惰目的估计也用python=。=

| URL                                                  | 调研结果                |
| ---------------------------------------------------- | ----------------------- |
| https://github.com/shekhargulati/flask-login-example | 纯登陆，调用flask-Login |
| https://github.com/tolgahanuzun/Flask-Login-Example  | 用来登陆ins的           |

安装依赖

```shell
pip3 install flask
pip3 install flask-login
```

问题解决

https://stackoverflow.com/questions/21701174/importerror-no-module-named-flask-ext-login

```python
from flask.ext.login import LoginManager
from flask_login import LoginManager
```

| 页面名称    | 介绍 |
| ----------- | ---- |
| 登陆页      |      |
| 主页面index |      |
| 注册页      |      |
|             |      |
|             |      |
|             |      |
|             |      |

