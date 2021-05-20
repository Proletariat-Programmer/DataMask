from flask import Flask, render_template, Response, redirect, url_for,\
    request, session, abort
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, \
    login_required, login_user, logout_user
import pdftopng # 内部引用
from pathlib import Path
import threading
import collections
import subprocess
import time
import os
import datetime
import pymysql
pymysql.install_as_MySQLdb()

# 全局变量
all_user_level = [0, 1, 2, 3, 4]
ready = 0
operating = 1
waiting = 2

app = Flask(__name__, static_folder="static")
# PyClone 处理记录文件
open_file_name = "log_pyclone.txt"

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# 这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名jianshu,连接方式参考 \
# http://docs.sqlalchemy.org/en/latest/dialects/mysql.html
# mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/test'
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


class User(UserMixin, db.Model):
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
    def __repr__(self):
        return "%d/%s/%s/%s" % (self.id, self.name, self.password, self.level)


    # def __repr__(self):
    #     return "%d/%s/%s/%s" % (self.id, self.name, self.phone, self.password)


class UploadFile(db.Model):
    # upload file system model
    # 定义表名
    __tablename__ = 'files'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 文件名称
    filename = db.Column(db.String(64),  index=True)
    # 上传患者名称
    up_name = db.Column(db.String(64),  index=True)
    # 上传患者性别
    up_sex = db.Column(db.String(64),  index=True)
    # 上传患者年龄
    up_age = db.Column(db.Integer,  index=True)
    # 上传患者联系方式
    up_phone = db.Column(db.String(64),  index=True)
    # 创建时间
    ctime = db.Column(db.DateTime,  default=datetime.datetime.utcnow)
    # 文件状态  0为已完成 1为进行中 2为排队中 其余为预料之外情况
    status = db.Column(db.Integer,  index=True)
    # 上传操作用户
    uid = db.Column(db.Integer,  index=True)

    def __init__(self, filename, status, uid, up_name, up_sex, up_age, up_phone):
        self.filename = filename
        self.status = status
        self.uid = uid
        self.up_name = up_name
        self.up_sex = up_sex
        self.up_age = up_age
        self.up_phone = up_phone


# 上传的任务队列
upload_task_id_list = collections.deque()

def check_level(user_id):
    # 以 user.level 来判断
    # 越接近0越厉害
    return User.query.filter_by(id=user_id).first().level

def check_admin(user_id):
    # 检测用户是否为管理员用户
    return True if  check_level(user_id) == 0 else False

def current_operate(current_file):
    # operate current upload file
    # 检测是否存在对应路径
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    my_file = Path(f'{basepath}/analysis_result/{str(current_file.uid)}')
    if not my_file.exists():
        # 检测是否存在id路径不存在
        os.makedirs(my_file)  # 只能创建单级目录 =.=对这个用法表示怀疑
        print(f'路径不存在 {my_file} 创建路径')

    # 初始化 pyclone 参数
    analysis_result_code = 0
    in_file_path = f'{basepath}/uploads/{str(current_file.uid)}/{current_file.filename}'
    working_dir_path = f'{basepath}/static/analysis_result/{str(current_file.uid)}/{current_file.filename}' # TODO 这里修改了待验证

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
    if analysis_result_code != 0:
        print("任务异常")

    # TODO 文件出炉
    pdftopng.loadall_pdf2png(current_file.uid, current_file.filename)

    # TODO 邮件通知功能
    turn_file_status_ready(current_file.id)     # 在这里把新的文件状态变更为已完成
    print("任务完成")

def operator_task():
    # 多线程处理任务队列
    while True:
        # 检测任务队列是否为空
        length_task_list = len(upload_task_id_list)
        if length_task_list != 0:
            print(upload_task_id_list)
            # 将任务队列的第一个弹出来送去处理, leftpop
            current_task = upload_task_id_list.popleft()
            print(f"当前任务 {current_task}")
            turn_file_status_operating(current_task.id)  # 在这里将 task 状态变更为 处理中
            current_operate(current_task)

        else:
            print("current task list is nil, retry after 1 minute")
        time.sleep(60)  # 一分钟检测一次


def turn_zip(filename):
    # 将目标文件压缩
    # subprocess
    try:
        print("start a new task")
        analysis_result_code = subprocess.run(
            ["zip", "参数"], stdout="test.log").returncode
    except:
        # 吃错误大法...
        analysis_result_code = 1



def register_add_user(username, password):
    #  level 4 - 最普通用户
    db.session.add(User(username, password, 4))
    db.session.commit()


def upload_add_file(upload_sql_obj):
    # tranfer upload file to the database
    db.session.add(upload_sql_obj)
    db.session.commit()


def turn_file_status_operating(upload_id):
    # turn status to operating
    current_file = UploadFile.query.get(upload_id)
    current_file.status = operating
    db.session.commit()


def turn_file_status_ready(upload_id):
    # turn status to ready
    current_file = UploadFile.query.get(upload_id)
    current_file.status = ready
    db.session.commit()


@app.route('/')
@login_required
def home():  # some protected url
    # return render_template("hello.html")
    # 判断是否为管理员以提供不同用户界面
    if check_admin(uid):
        return render_template("admin_index.html")
    else:
        return render_template("user_index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # somewhere to login
    if request.method == 'POST':
        login_info = request.form.to_dict()
        user = User.query.filter_by(name=login_info.get("username")).first()

        if user:  # 用户存在 且 密码相同
            if user.password == login_info.get("password"):
                login_user(user)
                print(f'用户登陆 {user.id} : {user.name}')
                return redirect("/history_list")

        return abort(401)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    # somewhere to logout
    logout_user()
    return render_template("logout.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # create new user
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
        print(
            f'新增用户 {login_info.get("username")} {login_info.get("password")}')

        # 新增用户
        # register_add_user(login_info.get("username"), login_info.get(
        #     "phone"), login_info.get("password"))
        register_add_user(login_info.get("username"), login_info.get("password"))

        return redirect("/login")
        # return redirect(request.args.get("next"))
    else:
        return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    # dashboard of system
    return render_template("dashboard.html")


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    # upload file
    if request.method == "POST":
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_info = request.form.to_dict()
        user_id = current_user.id
        print(f'当前登陆用户id {user_id}')

        # 检测是否存在对应路径
        my_file = Path(f'{basepath}/uploads/{str(user_id)}')
        if my_file.is_dir():
            # 存在
            print(f'路径存在 {my_file}')
        else:
            # 不存在
            os.mkdir(my_file)  # 只能创建单级目录
            print(f'路径不存在 {my_file}')

        # upload_path = os.path.join(basepath,"/uploads",secure_filename(f.filename))  #注意:没有的文件夹一定要先创建,不然会提示没有该路径
        f.save(f'{basepath}/uploads/{str(user_id)}/{secure_filename(f.filename)}')

        # 文件保存成功后,将此文件送入list
        # 创建文件类型
        # filename, ctime, status, uid
        
        up_name = upload_info.get("up_name")
        up_sex = upload_info.get("up_sex")
        up_age = upload_info.get("up_age")
        up_phone = upload_info.get("up_phone")

        upload_obj = UploadFile(secure_filename(
            f.filename), waiting, user_id, up_name, up_sex, int(up_age), up_phone)

        # 入库
        upload_add_file(upload_obj)

        # TODO 不能直接 传入文件对象id 因为要先入库再查询
        # TODO 直接通过 id 查询
        up_load_file_obj = UploadFile.query.filter_by(
            filename=f.filename).filter_by(
            uid=user_id).first()

        # threading多线程消息队列
        upload_task_id_list.append(up_load_file_obj)
        print(f'当前队列长度 {len(upload_task_id_list)}')
        print(upload_task_id_list)

        return redirect("/history_list")

    return render_template("upload.html")


@app.route("/upload_success")
@login_required
def upload_success():
    # upload success
    # 上传成功
    return render_template("upload_success.html")


@app.route("/history_list") # 注册路由 
@login_required # 需要登陆才能访问，否则强制转到login登陆界面
def history_list():
    # 历史上传记录
    uid = current_user.id

    # basepath = os.path.dirname(__file__)  # 当前文件所在路径
    # 检测是否存在对应路径,读取list
    # my_file = Path(f'{basepath}/uploads/{str(uid)}')
    # file_name_list = os.listdir(my_file) if my_file.is_dir() else []

    file_list = UploadFile.query.filter_by(uid=uid).all()

    # return render_template("history_list.html", history_list = file_name_list)
    return render_template("history_list.html", history_list=file_list, uid = uid)



@app.route("/level", methods=["GET", "POST"])
@login_required
def manager_user():
    # 非管理员用户直接弹回主界面
    if not check_admin(current_user.id):
        return redirect("/")

    # 拉取全部用户信息进行展示
    all_info = User.query.all()

    if request.method == "POST":
        # 获取提交数据
        search_info = request.form.to_dict()
        # 修改用户数据
        user = User.query.get(search_info.get("reid"))
        user.level = int(search_info.get("re_level"))
        db.session.commit()
        # 重置页面
        return redirect("/level")

    return render_template("level.html", all_info=all_info)


# 用于分析结果的展示
@app.route("/analysis_result/<uploadname>")
@login_required
def analysis_result(uploadname):
    pass
    # TODO 通过file_id 直接展示对应的分析结果

    # TODO 对file_id 是否属于此用户 , 文件状态是否为ready 进行判断

    # 查询其他Upload时传递的信息
    up_obj = UploadFile.query.filter_by(uid=current_user.id).filter_by(uploadname=uploadname).first()

    return render_template("analysis_result.html", uid=current_user.id, uploadname=uploadname, up_obj=up_obj)

# 用于分析结果的展示
@app.route("/result/<uploadname>")
@login_required
def temp_result(uploadname):
    return render_template("result.html", uid=current_user.id, uploadname=uploadname)



# @login_required
@app.route("/download/<uid>/<uploadname>/<bigfiletype>/<smallfiletype>/<filename>", methods=['GET'])
# 不查数据库,通uploadname过uid + type + filename直接拼出来目标文件位置
def download_file(uid, uploadname, bigfiletype, smallfiletype, filename):

    # object_file_path = f'analysis_result/{str(current_user.id)}/{uploadname}/{smallfiletype}/{filename}'
    object_file_path = f'analysis_result/{uid}/{uploadname}/{bigfiletype}/{smallfiletype}/{filename}'
    if bigfiletype == "tables":
        object_file_path = f'analysis_result/{uid}/{uploadname}/{bigfiletype}/{filename}'

    # filepath是文件的路径，但是文件必须存储在static文件夹下， 比如images\test.jp
    return app.send_static_file(object_file_path)


# 垃圾代码,仅展示一个图片
@app.route("/tip")
def tip():
    return app.send_static_file("css/tip.png")


@app.route("/pic/<picture_name>")
def pic_root(picture_name):
    return app.send_static_file(f'css/picture/{ picture_name }')



@app.errorhandler(401)
def page_not_found(e):
    # handle login failed
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    user = User.query.get(userid)  # get为主键查询
    return user


if __name__ == "__main__":
    # TODO 测试operator_task
    threading_task = threading.Thread(target=operator_task)
    threading_task.start()

    app.debug = True  # 开启快乐幼儿源模式
    app.run()
