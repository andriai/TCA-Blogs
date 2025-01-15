from ext import app
from routes import main, home, blogs, create_blog, blog_detail, login, register, logout, About, delete_blog, admin_dashboard, change_role, search


app.run(debug=True, host="0.0.0.0")
