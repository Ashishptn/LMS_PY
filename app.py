from flask import Flask, render_template, request, redirect, session, url_for, flash
from db_config import get_connection
from flask_session import Session
from aspnet_password import verify_aspnet_password
from db_config import get_menu_items
from user import user_blueprint





app = Flask(__name__)
app.secret_key = "6e6bad26cb7e0974318af3271bbf4453556bcb1b7900b3b1819724d67e4a6cf6"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.register_blueprint(user_blueprint)

def build_menu_dict(menu_items):
    menu_dict = {}
    for item in menu_items:
        parent_id = item.get("ParentId")
        if parent_id not in menu_dict:
            menu_dict[parent_id] = []           
        if parent_id in menu_dict:
            menu_dict[parent_id].append(item)

    return menu_dict


@app.route("/routes")
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:30s} {methods:20s} {rule}")
        output.append(line)
    return "<pre>" + "\n".join(sorted(output)) + "</pre>"


@app.context_processor
def inject_menu():
    menu_items = get_menu_items()
    menu_dict = build_menu_dict(menu_items)
    main_menus = menu_dict.get(None, []) + menu_dict.get(0, [])
    return dict(main_menus=main_menus, sub_menus=menu_dict)



@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error = "Please enter both username and password."
            return render_template('login.html', error=error)

        conn = get_connection()
        cursor = conn.cursor()

        # Corrected column: UserName instead of Username
        cursor.execute("SELECT UserName, PasswordHash FROM Rekhta_V5.dbo.AspNetUsers WHERE UserName = ?", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            db_username, db_password_hash = user

            if verify_aspnet_password(password, db_password_hash):
                session["username"] = db_username
                print("===== Login Successful =====")
                print("Logged in as:", db_username)
                return redirect('/dashboard')
            else:
                print("Not Login", db_username)
                error = "Invalid Login password"
        else:
            error = "User not found"
    return render_template('login.html', error=error)





def build_menu_dict(menu_items):
    menu_dict = {}
    for item in menu_items:
        parent_id = item.get("ParentId")
        if parent_id not in menu_dict:
            menu_dict[parent_id] = []
        menu_dict[parent_id].append(item)
    return menu_dict

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    menu_items = get_menu_items()
    menu_dict = build_menu_dict(menu_items)
    main_menus = menu_dict.get(None, []) + menu_dict.get(0, [])

    return render_template("layouts/base.html", main_menus=main_menus, sub_menus=menu_dict)

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)

    