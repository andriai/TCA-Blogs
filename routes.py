from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, current_user, login_required

from form import RegisterForm, LoginForm, BlogForm, CommentForm
from models import User, Blog, bcrypt, Comment, Like
from ext import app, db


@app.route("/")
def main():
    print("MAIN PAGE OPENED")
    return render_template("main.html")


@app.route("/Home")
@login_required
def home():
    return render_template("home.html")


@app.route("/Blogs", methods=['GET', 'POST'])
def blogs():
    blogs = Blog.query.all()
    sort_by = request.args.get('sort_by', 'recent')

    if sort_by == 'recent':
        blogs = Blog.query.order_by(Blog.id.desc()).all()
    elif sort_by == 'most_liked':
        blogs = Blog.query.join(Like, Blog.id == Like.blog_id) \
            .group_by(Blog.id) \
            .order_by(db.func.count(Like.id).desc()).all()

    return render_template("blogs.html", blogs=blogs, sort_by=sort_by)


@app.route("/Create_blog", methods=["GET", "POST"])
@login_required
def create_blog():
    form = BlogForm()

    if form.validate_on_submit():
        new_blog = Blog(title=form.title.data,
                        content=form.content.data,
                        author=current_user.username)
        new_blog.create()
        print(f"User {new_blog.author} created blog")
        return redirect("/")
    print(form.errors)

    return render_template('createblog.html', form=form)


@app.route('/blog_detail/<int:blog_id>', methods=['GET', 'POST'])
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    comments = Comment.query.filter_by(blog_id=blog.id).all()

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_comment = Comment(content=content, blog_id=blog.id, user_id=current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('blog_detail', blog_id=blog.id))

    return render_template('blog_detail.html', blog=blog, comments=comments)


@app.route('/like_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def like_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    like = Like.query.filter_by(user_id=current_user.id, blog_id=blog.id).first()

    if like:
        db.session.delete(like)
    else:
        new_like = Like(user_id=current_user.id, blog_id=blog.id)
        db.session.add(new_like)

    db.session.commit()

    return redirect("/Blogs")


@app.route("/Login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if user is not None and user.username == form.username.data and bcrypt.check_password_hash(user.password_hash,
                                                                                                   form.password.data):
            login_user(user)
            print(f"User {user.username} authorised successfully")
            return redirect("/")
    print(form.errors)

    return render_template('login.html', form=form)


@app.route("/Signup", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Hash password

        new_user = User(username=form.username.data,
                        email=form.email.data,
                        birth_date=form.birth_date.data,
                        password_hash=hashed_password,
                        role="Admin")
        new_user.create()
        login_user(new_user)
        print(f"User {new_user.username} registered successfully")
        return redirect("/")
    print(form.errors)

    return render_template('registration.html', form=form)


@app.route("/Logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/About")
def About():
    return render_template('about.html')


@app.route('/delete_blog/<int:blog_id>', methods=['GET', 'POST'])
def delete_blog(blog_id):
    if current_user.role != 'Admin':
        flash('Unauthorized action!', 'danger')
        return redirect("/Blogs")
    blog = Blog.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog deleted successfully!', 'success')
    return redirect('/Blogs')


@app.route("/Admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect("/")

    users = User.query.all()

    return render_template("admin_dashboard.html", users=users)


@app.route('/change_role/<int:user_id>', methods=['POST'])
@login_required
def change_role(user_id):
    if current_user.role != "Admin":
        flash("Unauthorized action!", "danger")
        return redirect("/Admin")

    user = User.query.get_or_404(user_id)
    new_role = request.form.get("new_role")

    if new_role not in ["User", "Admin"]:
        flash("Invalid role selected!", "danger")
        return redirect("/Admin")

    user.role = new_role
    db.session.commit()
    flash(f"Updated role for {user.username} to {new_role}!", "success")
    return redirect("/Admin")


@app.route("/Search")
def search():
    username = request.args.get("n", "").strip()
    user_id = request.args.get("id", "").strip()

    query = User.query

    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))

    if user_id:
        query = query.filter(User.id == user_id)

    users = query.all()

    return render_template("admin_dashboard.html", users=users)
