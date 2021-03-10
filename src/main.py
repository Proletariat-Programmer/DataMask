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

app = Flask(__name__, static_folder="static")

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

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# upload file system model
class UploadFile():

    def __init__(self, user_id, filename):
        self.user_id = user_id
        self.filename = filename

# create some users with ids 1 to 20
# users = [User(id) for id in range(1, 21)]

# 上传的任务队列
upload_task_list = collections.deque()

# operate current upload file
def current_operate(current_file):
    print(current_file.user_id)
    print(current_file.filename)

    time.sleep(3)

    # 检测是否存在对应路径
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    my_file = Path(f'{basepath}/analysis_result/{str(current_file.user_id)}')
    if my_file.is_dir():
        pass
    else:
        # 不存在
        os.mkdir(my_file) # 只能创建单级目录
        print(f'路径不存在 {my_file} 创建路径')

    # TODO 创建一个空文件先占位, 后续修改之
    # TODO 调研分析在更新后是否还需要这一步
    fd = open(f'{basepath}/analysis_result/{str(current_file.user_id)}/test.txt')
    fd.close()

    # 初始化 pyclone 参数
    analysis_result_code = 0
    in_file_path = ""
    working_dir_path = ""

    # 调用 pyclone
    try:
        analysis_result_code = subprocess.run(f'PyClone run_analysis_pipeline --in_files {in_file_path}  --working_dir {working_dir_path}').returncode
    except:
        # 吃错误大法...
        analysis_result_code = 1

    # 不为零代表出现异常情况
    if analysis_result_code != 0 :
        print("任务异常")
        return

    print("任务完成")
    return

# 多线程处理任务队列
def operator_task():
    print("hello this is a test")
    while True:
        # 检测任务队列是否为空
        length_task_list = len(upload_task_list)
        if length_task_list == 0 :
            print("当前任务队列为空, 一分钟后重试")
            time.sleep(3) # 一分钟后重试
            continue

        # 将任务队列的第一个弹出来送去处理, leftpop
        current_task =  upload_task_list.popleft()
        current_operate(current_task)

        time.sleep(60)

# operator add register
def register_add_user(username, phone, password):
    name = "user" + str(id)
    phone = id
    password = name + "pw"
    # init_user = User(id, name, phone, password)
    db.session.add(User(name, phone, password))
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

        if user :        # 用户存在 且 密码相同
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
        upload_obj = UploadFile(user_id, secure_filename(f.filename))
        upload_task_list.append(upload_obj)

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
