from flask import Blueprint, render_template, request, redirect, url_for, flash
from db_config import get_connection
from werkzeug.utils import secure_filename
from db_config import get_connection
import os
import uuid
from utils.password_hasher import hash_password_aspnet_core

user_blueprint = Blueprint('user_blueprint', __name__, url_prefix='/User')

UPLOAD_FOLDER = 'static/uploads'  # Adjust to your desired path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_blueprint.route('/ManageUser')
def manage_user():
    # Get current page from query string
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor()

    # Call the stored procedure with offset and fetch
    cursor.execute("EXEC SP_GetUserDetails_py ?, ?", (offset, per_page))
    users = cursor.fetchall()

    # Move to next result set to fetch total count
    cursor.nextset()
    total_records = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    total_pages = (total_records + per_page - 1) // per_page

    return render_template(
        "User/ManageUser.html",
        users=users,
        page=page,
        total_pages=total_pages
    )


@user_blueprint.route('/UserRole')
def manage_role():
    # Get current page from query string
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor()

    # Call the stored procedure with offset and fetch
    cursor.execute("EXEC SP_GetUserRoles_py ?,?, ?, ?", ('','',offset, per_page))
    roles = cursor.fetchall()
    
    # Move to next result set to fetch total count
    cursor.nextset()
    total_records = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    total_pages = (total_records + per_page - 1)
    print(roles)
    return render_template(
        "user/UserRole.html",
        roles=roles,
        page=page,
        total_pages=total_pages
    )

@user_blueprint.route('/Register', methods=['GET', 'POST'])
def register():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        postal = request.form.get('postal')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        image_file = request.files.get('image')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(request.url)

        # 🔒 Generate ASP.NET-compatible hash
        hashed_password = hash_password_aspnet_core(password)

        image_filename = None
        if image_file and image_file.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            image_file.save(image_path)
            image_filename = unique_filename
            print(f"[DEBUG] Uploaded Image Name: {image_filename}")

        try:            
            cursor.execute(
                "EXEC SP_REGISTERUSER_PY ?,?,?,?,?,?,?,?,?,?",
                (email, name, phone, street, city, state, postal, hashed_password, role, image_filename)
            )
            conn.commit()
            print("User registered successfully:", email)
            flash('User registered successfully!', 'success')
            return redirect(url_for('user_blueprint.manage_user'))

        except Exception as e:
            conn.rollback()
            print("Error saving user:", e)
            flash(f"Error saving user: {e}", 'danger')
        finally:
            cursor.close()
            conn.close()

    # For GET request: Load roles
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_GetAllRoles_py")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('User/Register.html', roles=roles, userid="00000000-0000-0000-0000-000000000000")

