'''

    快速脚本 - 数据库用户登陆模块  
    可快速 删表 并 建表 同时 导入20个默认用户

'''
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = '123456'
    database = 'test'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % (user,password,database)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % ("root","123456","test")
    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True

    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

# 读取配置
app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)

# class Role(db.Model):
#     # 定义表名
#     __tablename__ = 'roles'
#     # 定义字段
#     id = db.Column(db.Integer, primary_key=True,autoincrement=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User',backref='role') # 反推与role关联的多个User模型对象

class AdminUp(db.Model):
    # 定义表名
    __tablename__ = 'adup'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 文件名称
    csvname = db.Column(db.String(64), index=True)
    # 上传患者名称
    up_name = db.Column(db.String(64), index=True)
    # 上传患者性别 0女 1男
    up_sex = db.Column(db.Integer, index=True)
    # 上传患者年龄
    up_age = db.Column(db.Integer, index=True)
    # 上传患者联系方式
    up_phone = db.Column(db.String(64), index=True)
    # 病例名称
    b_name = db.Column(db.String(150), index=True)
    # 创建时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, csvname, up_name, up_sex, up_age, up_phone, b_name):
        self.csvname = csvname
        self.up_name = up_name
        self.up_sex = int(up_sex)
        self.up_age = int(up_age)
        self.up_phone = up_phone
        self.b_name = b_name


class Download(db.Model):
    # 定义表名
    __tablename__ = 'download'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 压缩包名称
    zip_name = db.Column(db.String(64), index=True)
    # 文件存储路径
    savepath = db.Column(db.String(64), index=True)
    # 权限管理
    level_require = db.Column(db.Integer, index=True)
    # 文件创建时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # 文件最后更新时间
    mtime = db.Column(db.DateTime, default=datetime.datetime.now,
                      onupdate=datetime.datetime.now)

    def __init__(self, zip_name, savepath, level_require):
        self.zip_name = zip_name
        self.savepath = savepath
        self.level_require = int(level_require)


# upload file system model
class UploadFile(db.Model):
    # 定义表名
    __tablename__ = 'files'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    # 文件名称
    filename = db.Column(db.String(64), index=True)
    # 上传患者名称
    up_name = db.Column(db.String(64), index=True)
    # 上传患者性别 0女 1男
    up_sex = db.Column(db.Integer, index=True)
    # 上传患者年龄
    up_age = db.Column(db.Integer, index=True)
    # 上传患者联系方式
    up_phone = db.Column(db.String(64), index=True)
    # 创建时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # 文件状态  0为已完成 1为进行中 2为排队中 其余为预料之外情况
    status = db.Column(db.Integer, index=True)
    # 用户id
    uid = db.Column(db.Integer, index=True)
    # 病例信息
    detail = db.Column(db.String(150), index=True)

    def __init__(self, filename, status, uid, up_name, up_sex, up_age, up_phone, detail):
        self.filename = filename
        self.status = status
        self.uid = uid
        self.up_name = up_name
        self.up_sex = int(up_sex)
        self.up_age = int(up_age)
        self.up_phone = up_phone
        self.detail = detail

class User(db.Model):
    # 定义表名
    __tablename__ = 'users'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(64), unique=True, index=True)

    # email = db.Column(db.String(64),unique=True)
    password = db.Column(db.String(64))
    # 操作时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now)
    # 最近更次时间
    mtime = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    # 用户权限登记 (0为管理员 非0为用户)
    level = db.Column(db.Integer, index=True)
    def __init__(self, name, password, level):
        self.name = name
        self.level = level 
        self.password = password

if __name__ == '__main__':

    # 删除所有表
    db.drop_all()

    # 创建所有表
    db.create_all()

    # 创建20个默认用户
    # create some users with ids 1 to 20
    for i in range(1, 21):
        level = 0 if i == 1 else 4
        id = i
        name = "user" + str(id)
        # phone = id
        password = name + "pw"
        db.session.add(User(name, password, level))
        db.session.commit()

    # 测试用例
    upload_obj = UploadFile("SRR385938.tsv", 0,2, "hello", 1, 30, 300132, "only a test")
    db.session.add(upload_obj)
    db.session.commit()

    # 用户x a
    # zipname, savepath, level_require
    down_obj = Download("t4.zip", "4/wy.zip", 4)
    db.session.add(down_obj)
    db.session.commit()

    down_obj = Download("t3.zip", "3/wy.zip", 3)
    db.session.add(down_obj)
    db.session.commit()

    down_obj = Download("t2.zip", "2/wy.zip", 2)
    db.session.add(down_obj)
    db.session.commit()

    down_obj = Download("t1.zip", "1/wy.zip", 1)
    db.session.add(down_obj)
    db.session.commit()


'''
初始化后效果展示

mysql> select * from users;
+----+--------+-------+----------+
| id | name   | phone | password |
+----+--------+-------+----------+
|  1 | user1  | 1     | user1pw  |
|  2 | user2  | 2     | user2pw  |
|  3 | user3  | 3     | user3pw  |
|  4 | user4  | 4     | user4pw  |
|  5 | user5  | 5     | user5pw  |
|  6 | user6  | 6     | user6pw  |
|  7 | user7  | 7     | user7pw  |
|  8 | user8  | 8     | user8pw  |
|  9 | user9  | 9     | user9pw  |
| 10 | user10 | 10    | user10pw |
| 11 | user11 | 11    | user11pw |
| 12 | user12 | 12    | user12pw |
| 13 | user13 | 13    | user13pw |
| 14 | user14 | 14    | user14pw |
| 15 | user15 | 15    | user15pw |
| 16 | user16 | 16    | user16pw |
| 17 | user17 | 17    | user17pw |
| 18 | user18 | 18    | user18pw |
| 19 | user19 | 19    | user19pw |
| 20 | user20 | 20    | user20pw |
+----+--------+-------+----------+
20 rows in set (0.00 sec)

'''
