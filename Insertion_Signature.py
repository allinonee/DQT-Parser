import hashlib
import os
import sqlite3

### 시작 ### 
connect_db_path = input("Enter the DB path to link => ")

# DB 연동
connect_db = sqlite3.connect(connect_db_path)
cursor_db = connect_db.cursor()

# [Func 2] DB 데이터 삽입 (editor, exif, DQThash)
Editor_NAME = input("Enter Editor Name => ")
Filename_SIG = input("Enter Editor Filename Signature => ")

cursor_db.execute('SELECT * FROM Editor_Filename')
raw_data = cursor_db.fetchall()
data = (Editor_NAME, Filename_SIG)

if data not in raw_data:
    cursor_db.execute("INSERT INTO Editor_Filename (editor, filename) VALUES (?, ?)", data)
    connect_db.commit()
    print('\033[31m' + "Data insertion is complete." + '\033[0m')
else:
    print('\033[31m' + "Data already exists." + '\033[0m')
