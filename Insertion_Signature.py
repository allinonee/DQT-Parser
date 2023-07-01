import hashlib
import os
import sqlite3

### 시작 ### 
connect_db_path = input("Enter the DB path to link => ")

# DB 연동
connect_db = sqlite3.connect(connect_db_path)
cursor_db = connect_db.cursor()

# 데이터 삽입 
editor = input("Enter editor name => ")
version = input("Enter editor version => ")
filename_sig = input("Enter editor filename signature => ")

cursor_db.execute('SELECT app_Id FROM Image_Editors WHERE editor_name = ? AND version = ?', (editor, version))
result = cursor_db.fetchone()

if result is not None:
    app_Id = result[0]

    cursor_db.execute('SELECT * FROM Editor_Signature')
    raw_data = cursor_db.fetchall()
    data = (app_Id, editor, version, filename_sig)

    if data not in raw_data:
        cursor_db.execute("INSERT INTO Editor_Signature (Id, editor, editor_version, signature) VALUES (?, ?, ?, ?)", data)
        connect_db.commit()
        print('\033[31m' + "Data insertion is complete." + '\033[0m')
    else:
        print('\033[31m' + "Data already exists." + '\033[0m')
