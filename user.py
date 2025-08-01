from flask import Blueprint, render_template
from db_config import get_connection
from db_config import get_menu_items
import os

user_blueprint = Blueprint('user', __name__, url_prefix='/User')

# @user_blueprint.route('/ManageUser')
# def manage_user():
    # return render_template('User/ManageUser.html')
def build_menu_dict(menu_items):
    menu_dict = {}
    for item in menu_items:
        parent_id = item.get("ParentId")
        if parent_id not in menu_dict:
            menu_dict[parent_id] = []
        menu_dict[parent_id].append(item)
    return menu_dict

@user_blueprint.route('/ManageUser')
def manage_user():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("exec SP_GetUserDetails_py")
    users = cursor.fetchall()   

    menu_items = get_menu_items()
    menu_dict = build_menu_dict(menu_items)
    main_menus = menu_dict.get(None, []) + menu_dict.get(0, [])
    conn.close()
    return render_template("User/ManageUser.html",menu_items=main_menus, sub_menus=menu_dict, users=users)