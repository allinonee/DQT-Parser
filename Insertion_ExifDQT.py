import hashlib
import os
import sqlite3

# JPEG 확인 & DQT 파싱
def dqt_parser(image_path):
    f = open(image_path, 'rb')
    data = f.read()  
    
    JPEG_SIG = b'\xff\xd8'
    DQT_SIG = b'\xff\xdb'

    if data[:2] == JPEG_SIG:
        dqt_idx_lst = []
        idx = 0
        while True:
            dqt_start_idx = data[idx:].find(DQT_SIG)
            if dqt_start_idx+idx not in dqt_idx_lst:
                dqt_idx_lst.append(dqt_start_idx+idx)
            else:
                break
            idx = dqt_start_idx + 1
        
        dqt = []
        for i in dqt_idx_lst:
            dqt_size = data[i+3]
            dqt_data = data[i:i+dqt_size+2] # dqt_size는 앞의 Marker 2바이트 제외하기 때문에 +2 필요
            dqt.append(dqt_data)
        return dqt 
    else:
        print("'{}' not a JPEG.".format(image_path))
        return 0

# DQT Hash(MD5) 계산
def calc_dqt_hash(dqt_list):
    hash_lst = []
    for i in dqt_list:
        dqt_hash = hashlib.md5(i).hexdigest()
        hash_lst.append(dqt_hash)
    return hash_lst

# Exif(Software, Artist) 정보 추출
def exiftool(image_path):
    exif = os.popen('.\exiftool.exe "{}"'.format(image_path)).readlines() 
    exif_lst = []
    for i in exif:
        if 'Software' in i:
            exif_lst.append(i.strip().split(':')[1])
        elif 'Artist' in i:
            exif_lst.append(i.strip().split(':')[1])
    return ', '.join(exif_lst) # list가 아닌, str으로 DB 삽입을 위함 


### 시작 ### 
connect_db_path = input("Enter the DB path to link => ")

# DB 연동
connect_db = sqlite3.connect(connect_db_path)
cursor_db = connect_db.cursor()

# [Func 2] DB 데이터 삽입 (editor, exif, DQThash)
folder = input("Enter Image folder path => ") + "\\" 
editor = input("Enter Editor Name => ")
image_folder_path = os.listdir(folder)

# 모든 이미지에 대해 (exif, hash) 형태로 리스트에 넣고, 중복 제거해서 DB에 삽입 
exif_hash_lst = []
for i in image_folder_path:
    dqt = dqt_parser(folder+i)
    if dqt != 0:
        hash = ', '.join(calc_dqt_hash(dqt))
        exif = exiftool(folder+i)
        exif_hash_lst.append((exif, hash))

exif_hash_lst = set(exif_hash_lst)
cursor_db.execute('SELECT * FROM Editor_DQT')
raw_data = cursor_db.fetchall()

# DB내 동일 내용이 없을 경우에만 INSERT O
for i in exif_hash_lst:
    data = (editor, i[0], i[1])
    if data not in raw_data:
        cursor_db.execute("INSERT INTO Editor_DQT (editor, exif, hash) VALUES (?, ?, ?)", data)
        connect_db.commit()

print('\033[31m' + "Data insertion is complete." + '\033[0m')

connect_db.close()