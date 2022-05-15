import flask_login
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, CreateRegisterForm, CreateLoginForm, CreateCommentForm
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES

Base=declarative_base()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # author = db.Column(db.String(250), nullable=False)
    author = relationship("User", back_populates="posts")
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment_author = relationship("User", back_populates="comments")
    comment_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parent_post = relationship("BlogPost", back_populates="comments")
    parent_post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    text = db.Column(db.Text, nullable=False)

db.create_all()

## Enable Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CreateRegisterForm()
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash('This email is already registered! Login instead!')
        else:
            try:
                hashed_pw = generate_password_hash(request.form['password'], method='pbkdf2:sha256',
                                                                 salt_length=8)
                new_user = User(
                    name = request.form['name'],
                    email = request.form['email'],
                    password = hashed_pw,
                )
                db.session.add(new_user)
                db.session.commit()
                print('new user created')
                login_user(new_user)
                return redirect(url_for('login'))
            finally:
                pass
    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = CreateLoginForm()
    if form.validate_on_submit() and request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                pw_check = check_password_hash(
                    pwhash=user.password,
                    password=request.form['password'],
                )
                print(pw_check)
                if pw_check == True:
                    flash('Successfully logged in!')
                    login_user(user)
                    return redirect(url_for('get_all_posts'))
                else:
                    flash('Incorrect Password.')
                    return redirect('login')
            else:
                flash('There is no account associated with that email.')
                return redirect('login')
        finally:
            pass
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['GET','POST'])
def show_post(post_id):
    comments = BlogPost.query.get(post_id).comments
    requested_post = BlogPost.query.get(post_id)
    comment_form = CreateCommentForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            db.session.add(Comment(
                comment_author_id=current_user.id,
                parent_post_id=post_id,
                text=comment_form.comment.data,
            ))
            db.session.commit()
        else:
            flash('You need to login to comment!')
    return render_template("post.html", post=requested_post, form=comment_form, comments=comments)


@app.route("/about")
def about():
    if flask_login.user_logged_in == True:
        print('true')
    print(flask_login.user_logged_in)
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=['GET','POST'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=['GET','POST'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    print(current_user.id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        # post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
