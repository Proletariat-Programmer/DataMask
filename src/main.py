import os
import time
import collections
import threading
from pathlib import Path

from flask import Flask,render_template, Response, redirect, url_for,\
                         request, session, abort
from flask_login import LoginManager, UserMixin, current_user, \
                                login_required, login_user, logout_user
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static")

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "pw"
        self.phone = "11112222333"
        # self.password = self.name + "_secret"
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

# upload file system model
class UploadFile():

    def __init__(self, user_id, filename):
        self.user_id = user_id
        self.filename = filename

class UpStatus():

    def __init__(self):
        self.current_status = 0 # [0-已完成 1-处理中 2-等待中]
        self.upstime = "" # 上传时间
        self.needtime = "" # 预计还要多久
        self.upoload_name = ""

# create some users with ids 1 to 20
users = [User(id) for id in range(1, 21)]

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
    fd = open(f'{basepath}/analysis_result/{str(current_file.user_id)}/test.txt')
    fd.close()

    # TODO 在这里调用conda gene 部分代码

    print("任务完成===================")

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

# some protected url
@app.route('/')
@login_required
def home():
    return render_template("hello.html")

# some protected url
@app.route('/index')
@login_required
def index():
    return render_template("index.html")


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        login_info = request.form.to_dict()
       # username = request.form['username']
       # phone = request.form['phone']
       # password = request.form['password']
        for item in users:
            # if (username == item.name or phone == item.phone) and password == item.password:
            if (login_info.get("username") == item.name or login_info.get("phone") == item.phone) and login_info.get("password") == item.password:
                user = User(item.id)
                login_user(user)
                print(f'用户登陆 id : {id}')
                # return redirect(request.args.get("next"))
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
        length_id = len(users) + 1
        users.append(User(length_id))
        f_length = len(users) - 1
        login_info = request.form.to_dict()
        users[f_length].name = login_info.get("username")
        users[f_length].phone = login_info.get("phone")
        users[f_length].password =login_info.get("password")

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
    return User(userid)

if __name__ == "__main__":
    # TODO 测试operator_task
    threading_task = threading.Thread(target = operator_task)
    threading_task.start()

    app.debug = True # 开启快乐幼儿源模式
    app.run()
