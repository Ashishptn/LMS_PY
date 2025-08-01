import pyodbc

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=10.60.7.55;'
        'DATABASE=RekhtaLearn-dev;'
        'UID=sa;'
        'PWD=P@ssw0rd'
    )
    return conn

def get_menu_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_GetMainMenu_py")
    #rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # print("== DEBUG: Raw menu items ==")
    # for r in rows:
        # print(r)

    return rows


    # Group by ParentId
    menu_dict = {}
    for row in rows:
        parent_id = row["ParentId"]
        if parent_id not in menu_dict:
            menu_dict[parent_id] = []
        menu_dict[parent_id].append(row)
    
    return menu_dict