from flask import Blueprint, render_template
from db_config import get_connection

user_blueprint = Blueprint('user_blueprint', __name__, url_prefix='/User')

@user_blueprint.route('/ManageUser')
def manage_user():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("exec SP_GetUserDetails_py")
    users = cursor.fetchall()
    conn.close()
    return render_template("User/ManageUser.html", users=users)
