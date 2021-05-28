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
    # level = db.Column(db.Integer, index=True)
    def __init__(self, name, password):
        self.name = name
        self.password = password


class Role(db.Model):
    # 定义表名
    __tablename__ = 'role'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 角色名称
    role_name = db.Column(db.String(64))

    # 操作时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now)
    # 最近更次时间
    mtime = db.Column(db.DateTime, default=datetime.datetime.now,
                      onupdate=datetime.datetime.now)

    def __init__(self, role_name):
        self.role_name = role_name


class Level(db.Model):
    # 定义表名
    __tablename__ = 'level'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 操作名
    operate = db.Column(db.String(64))

    # 操作时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now)
    # 最近更次时间
    mtime = db.Column(db.DateTime, default=datetime.datetime.now,
                      onupdate=datetime.datetime.now)

    def __init__(self, operate):
        self.operate = operate


class UserRole(db.Model):
    # 定义表名
    __tablename__ = 'u_r'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 关联用户
    uid = db.Column(db.Integer, index=True)
    # 关联角色
    rid = db.Column(db.Integer, index=True)

    # 操作时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now)
    # 最近更次时间
    mtime = db.Column(db.DateTime, default=datetime.datetime.now,
                      onupdate=datetime.datetime.now)

    def __init__(self, uid, rid):
        self.uid = uid
        self.rid = rid


class LevelRole(db.Model):
    # 定义表名
    __tablename__ = 'l_r'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 权限
    lid = db.Column(db.Integer, index=True)
    # 角色
    rid = db.Column(db.Integer, index=True)

    # 操作时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now)
    # 最近更次时间
    mtime = db.Column(db.DateTime, default=datetime.datetime.now,
                      onupdate=datetime.datetime.now)

    def __init__(self, lid, rid):
        self.lid = lid
        self.rid = rid


if __name__ == '__main__':

    # 删除所有表
    db.drop_all()

    # 创建所有表
    db.create_all()

    # 测试用例
    upload_obj = UploadFile("SRR385938.tsv", 0,2, "hello", 1, 30, 300132, "only a test")
    db.session.add(upload_obj)
    db.session.commit()

    # 用户x a
    # zipname, savepath, level_require
    # K2
    down_obj = Download("t4.zip", "4/wy.zip", 2)
    db.session.add(down_obj)
    db.session.commit() 
    # K2L2
    down_obj = Download("t3.zip", "3/wy.zip", 3)
    db.session.add(down_obj)
    db.session.commit()
    # K2T2
    down_obj = Download("t2.zip", "2/wy.zip", 4)
    db.session.add(down_obj)
    db.session.commit()
    # K10
    down_obj = Download("t1.zip", "1/wy.zip", 5)
    db.session.add(down_obj)
    db.session.commit()


    # level 权限表初始化
    db.session.add(Level("K2-Show")) # 1
    db.session.commit()
    db.session.add(Level("K10-Show")) # 2
    db.session.commit()
    db.session.add(Level("K2L2-Show")) # 3
    db.session.commit()
    db.session.add(Level("K2P2-Show")) # 4
    db.session.commit()
    db.session.add(Level("K2-Download")) # 5
    db.session.commit()
    db.session.add(Level("K10-Download")) # 6
    db.session.commit()
    db.session.add(Level("K2L2-Download")) # 7
    db.session.commit()
    db.session.add(Level("K2P2-Download"))# 8
    db.session.commit()

    # role 角色表初始化
    db.session.add(Role("admin")) # 1
    db.session.commit()
    db.session.add(Role("user-K2")) # 2
    db.session.commit()
    db.session.add(Role("user-K2L2")) # 3
    db.session.commit()
    db.session.add(Role("user-K2T2")) # 4
    db.session.commit()
    db.session.add(Role("user-K10")) # 5
    db.session.commit()
    # 以上id均从1开始计数

    # 用户表初始化
    # create some users with ids 1 to 20
    for i in range(1, 21):
        name = "user" + str(i)
        password = name + "pw"
        db.session.add(User(name, password))
        db.session.commit()

    # u_r 用户角色表初始化
    for i in range(1, 21):
        if i == 1:
            db.session.add(UserRole(i, 1))  # 1
            db.session.commit()
        else:
            db.session.add(UserRole(i, 2))  # 1
            db.session.commit()

    # l_r 角色权限表初始化
    for i in range(1, 9): # 管理员 - 8种权限
        db.session.add(LevelRole(i, 1))  # 1
        db.session.commit()
    
    # K2P2 
    db.session.add(LevelRole(4, 1))  # 2
    db.session.commit()
    db.session.add(LevelRole(8, 1))  # 2
    db.session.commit()

    # K2L2
    db.session.add(LevelRole(3, 1))  # 3
    db.session.commit()
    db.session.add(LevelRole(7, 1))  # 3
    db.session.commit()

    # K10
    db.session.add(LevelRole(2, 1))  # 4
    db.session.commit()
    db.session.add(LevelRole(6, 1))  # 4
    db.session.commit()

    # K2
    db.session.add(LevelRole(1, 1))  # 5
    db.session.commit()
    db.session.add(LevelRole(5, 1))  # 5
    db.session.commit()


    # test
    ur = UserRole.query.filter_by(uid=4).first()
    ur.rid = 3
    db.session.commit()

    print("结束")



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
