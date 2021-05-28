'''

    数据批量导入脚本  
    针对给定csv文件,同步导入MySQL与总CSV

'''

# 用于文件追加写入
import pandas as pd

import csv
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from werkzeug.utils import secure_filename
pymysql.install_as_MySQLdb()

app = Flask(__name__)


class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = '123456'
    database = 'test'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % (
        user, password, database)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % ("root","123456","test")
    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    # app.config['SQLALCHEMY_ECHO'] = True

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


if __name__ == '__main__':
    # 读取csv文件
    # with open(f"k2.csv", "r") as file:
    with open(f"static/upload_data/data.csv", "r") as file:
        with open(f"static/upload_data/data3.csv", "a+") as file2:
            # csv 追加写入

            rd = csv.reader(file)
            headers = next(rd)
            t = 0
            for item in rd:
                t+= 1
                # 对每个数据进行新增数据插入
                print(item)
                # 创建对象并入库
                sex = 1 if item[3] == 'Male' else 0

                data_add = {'name': [str(item[0])],
                            'age': [str(item[1])],
                            'fnlwgt': [str(item[2])],
                            'sex': [str(item[3])],
                            'disease': [str(item[4])],
                            'csv_name': [str(item[5])]}
                print(data_add)
                df_add = pd.DataFrame(data=data_add, index=[0])

                # a-add追加写入
                df_add.to_csv("static/upload_data/data2.csv",
                            mode='a', header=False, index=False)

                upload_obj = AdminUp(
                    item[5], item[0], sex, item[1], item[2], item[4])
                db.session.add(upload_obj)
                db.session.commit()

        print(f"导入结束, 共计{t}条")
