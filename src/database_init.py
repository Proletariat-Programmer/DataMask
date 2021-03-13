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

# upload file system model
class UploadFile(db.Model):
    # 定义表名
    __tablename__ = 'files'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    # 文件名称
    filename = db.Column(db.String(64),  index=True)
    ctime = db.Column(db.DateTime,  default=datetime.datetime.utcnow)
    # 文件状态  0为已完成 1为进行中 2为排队中 其余为预料之外情况
    status = db.Column(db.Integer,  index=True)
    uid = db.Column(db.Integer,  index=True)

    def __init__(self, filename, status, uid):
        self.filename = filename
        self.status = status
        self.uid = uid

class User(db.Model):
    # 定义表名
    __tablename__ = 'users'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(64), unique=True, index=True)
    phone = db.Column(db.String(64),unique=True)
    # email = db.Column(db.String(64),unique=True)
    password = db.Column(db.String(64))
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 设置外键
    def __init__(self, name, phone, password):
        self.name = name
        self.phone = phone
        self.password = password

if __name__ == '__main__':

    # 删除所有表
    db.drop_all()

    # 创建所有表
    db.create_all()

    # 创建20个默认用户
    # create some users with ids 1 to 20
    for i in range(1, 21):
        id = i
        name = "user" + str(id)
        phone = id
        password = name + "pw"
        db.session.add(User(name, phone, password))
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
