import os
from flask import Flask,render_template, Response, redirect, url_for, request, session, abort
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user
from werkzeug.utils import secure_filename

app = Flask(__name__)

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

# create some users with ids 1 to 20
users = [User(id) for id in range(1, 21)]

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
       # username = request.form['username']
       # phone = request.form['phone']
       # password = request.form['password']
        for item in users:
            # if (username == item.name or phone == item.phone) and password == item.password:
            if (login_info.get("username") == item.name or login_info.get("phone") == item.phone) and login_info.get("password") == item.password:
                id = item.id
                user = User(id)
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
    global user
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
def dashboard():
    return render_template("dashboard.html")

# upload file
@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        print(basepath)
        upload_path = os.path.join(basepath, '/uploads',secure_filename(f.filename))  #注意:没有的文件夹一定要先创建,不然会提示没有该路径
        f.save(upload_path)
        return redirect(url_for('upload'))

    return render_template("upload.html")

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)

if __name__ == "__main__":
    app.debug = True # 开启快乐幼儿源模式
    app.run()
