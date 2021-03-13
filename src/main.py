import pymysql
pymysql.install_as_MySQLdb()

import os
import time
import subprocess
import collections
import threading
from pathlib import Path

from flask import Flask,render_template, Response, redirect, url_for,\
                         request, session, abort
from flask_login import LoginManager, UserMixin, current_user, \
                                login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

const ready = 0
const operating = 1
const waiting = 2

app = Flask(__name__, static_folder="static")
# pyclone处理记录
open_file_name = "test.txt"

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# 这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名jianshu,连接方式参考 \
# http://docs.sqlalchemy.org/en/latest/dialects/mysql.html
# mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:123456@127.0.0.1:3306/test'
# 设置sqlalchemy自动更跟踪数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 查询时会显示原始SQL语句
app.config['SQLALCHEMY_ECHO'] = True
# 禁止自动提交数据处理
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
# 创建SQLAlichemy实例
db = SQLAlchemy(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin, db.Model):
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
        # self.id = id
        self.name = name
        self.phone = phone
        self.password = password
    def __repr__(self):
        return "%d/%s/%s/%s" % (self.id, self.name, self.phone, self.password)

# upload file system model
class UploadFile(db.Model):
    # 定义表名
    __tablename__ = 'files'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 文件名称
    filename = db.Column(db.String(64),  index=True)
    ctime = db.Column(db.DateTime,  index=True)
    # 文件状态  0为已完成 1为进行中 2为排队中 其余为预料之外情况
    status = db.Column(db.Integer,  index=True)
    uid = db.Column(db.Integer,  index=True)

    def __init__(self, filename, ctime, status, uid):
        self.filename = filename
        self.ctime = ctime
        self.status = status
        self.uid = uid

# 上传的任务队列
upload_task_list = collections.deque()

# operate current upload file
def current_operate(current_file):

    # 检测是否存在对应路径
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    my_file = Path(f'{basepath}/analysis_result/{str(current_file.user_id)}')
    if not my_file.exists():
        # 检测是否存在id路径不存在
        os.makedirs(my_file)  # 只能创建单级目录 =.=对这个用法表示怀疑
        print(f'路径不存在 {my_file} 创建路径')

    # 初始化 pyclone 参数
    analysis_result_code = 0
    in_file_path = f'{basepath}/uploads/{str(current_file.user_id)}/{current_file.filename}'
    working_dir_path = f'{basepath}/analysis_result/{str(current_file.user_id)}/{current_file.filename}'

    # 打开一个文件作为收集途径
    with open(open_file_name, "w+") as file:
        # 调用 pyclone
        try:
            print("start a new task")
            analysis_result_code = subprocess.run(
                ["PyClone", "run_analysis_pipeline",
                "--in_files", f'{in_file_path}',
                "--working_dir", f'{working_dir_path}'], stdout=file).returncode
        except:
            # 吃错误大法...
            analysis_result_code = 1

    # 不为零代表出现异常情况
    if analysis_result_code != 0 :
            print("任务异常")

    print("任务完成")
    turn_file_status_ready(current_file)     # 在这里把新的文件状态变更为已完成

# 多线程处理任务队列
def operator_task():
    while True:
        # 检测任务队列是否为空
        length_task_list = len(upload_task_list)
        if length_task_list != 0:
            # 将任务队列的第一个弹出来送去处理, leftpop
            current_task =  upload_task_list.popleft()
            turn_file_status_operating(current_task)  # 在这里将 task 状态变更为 处理中
            current_operate(current_task)
        else:
            print("current task list is nil, retry after 1 minute")
        time.sleep(60)

# operator add register
def register_add_user(username, phone, password):
    # name = "user" + str(id)
    # phone = id
    # password = name + "pw"
    db.session.add(User(username, phone, password))
    db.session.commit()

# tranfer upload file to the database 
def upload_add_file(upload_obj):
    db.session.add(UploadFile(upload_obj))
    db.session.commit()

# turn status to operating
def turn_file_status_operating(upload_obj):
    current_file = UploadFile.query.get(upload_obj)
    current_file.status = operating
    db.session.add(UploadFile(upload_obj))
    db.session.commit()

# turn status to ready
def turn_file_status_ready(upload_obj):
    current_file = UploadFile.query.get(upload_obj)
    current_file.status = ready
    db.session.add(UploadFile(upload_obj))
    db.session.commit()

# some protected url
@app.route('/')
@login_required
def home():
    return render_template("hello.html")

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        login_info = request.form.to_dict()
        user = User.query.filter_by(name = login_info.get("username")).first()

        if user :  # 用户存在 且 密码相同
            if user.password == login_info.get("password"):
                login_user(user)
                print(f'用户登陆 {user.id} : {user.name}')
                return redirect("/")

        return abort(401)
    else:
        return render_template("login.html")

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")

# creater new user
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login_info = request.form.to_dict()
        # TODO 重名检测未添加
        # 查询是否有重名 & 是否有
        # user_name = User.query.filter_by(name = login_info.get("username")).first()
        # user_phone = User.query.filter_by(name = login_info.get("phone")).first()

        # TODO register 里面 携带status_code 以及 source
        # if not user_name :
        #     return render_template("register.html")
        # elif not user_phone:
        #     return render_template("register.html")
        # else:
        print(f'新增用户 {login_info.get("username")} {login_info.get("phone")} {login_info.get("password")}')

        # 新增用户
        register_add_user(login_info.get("username"), login_info.get("phone"), login_info.get("password"))

        return redirect("/login")
        # return redirect(request.args.get("next"))
    else:
        return render_template("register.html")

# dashboard of system
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# upload file
@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')

        # 检测是否存在对应路径
        my_file = Path(f'{basepath}/uploads/{str(user_id)}')
        if my_file.is_dir():
            # 存在
            print(f'路径存在 {my_file}')
        else:
            # 不存在
            os.mkdir(my_file) # 只能创建单级目录
            print(f'路径不存在 {my_file}')

        # upload_path = os.path.join(basepath,"/uploads",secure_filename(f.filename))  #注意:没有的文件夹一定要先创建,不然会提示没有该路径
        f.save(f'{basepath}/uploads/{str(user_id)}/{secure_filename(f.filename)}')

        # 文件保存成功后,将此文件送入list
        # filename, ctime, status, uid
        upload_obj = UploadFile(secure_filename(
            f.filename), "time", waiting, user_id)

        # 只把id传入
        upload_task_list.append(upload_obj.id)

        return redirect("upload_success.html")

    return render_template("upload.html")

# upload success
@app.route("/upload_success")
@login_required
def upload_success():
    # 上传成功
    return render_template("upload_success.html")

# history list
@app.route("/history_list")
@login_required
def history_list():
    # 历史上传记录
    user_id = current_user.id
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    # 检测是否存在对应路径,读取list
    my_file = Path(f'{basepath}/uploads/{str(user_id)}')
    file_name_list = os.listdir(my_file) if my_file.is_dir() else []

    return render_template("history_list.html", history_list = file_name_list)


# 用于分析结果的展示
@app.route("/analysis_result")
@login_required
def analysis_result():
    pass
    return

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    user = User.query.get(userid) # get为主键查询
    return user

if __name__ == "__main__":
    # TODO 测试operator_task
    threading_task = threading.Thread(target = operator_task)
    threading_task.start()

    app.debug = True # 开启快乐幼儿源模式
    app.run()
