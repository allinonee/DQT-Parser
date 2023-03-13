import hashlib
import os
import sqlite3

# JPEG 확인 & DQT 파싱
def dqt_parser(image_path):
    f = open(image_path, 'rb')
    data = f.read()  
    
    jpeg_sig = b'\xff\xd8'
    if data[:2] == jpeg_sig:
        dqt_idx_lst = []
        idx = 0
        while True:
            dqt_start_idx = data[idx:].find(b'\xff\xdb')
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


## 시작 ### 
connect_db_path = input("Enter the DB path to link => ")

# DB 연동
connect_db = sqlite3.connect(connect_db_path)
cursor_db = connect_db.cursor()

# [Func 1] 이미지 마지막 출처 확인
image = input('Checking the Last source of Image (input image path) => ')
dqt = dqt_parser(image)
hash = ', '.join(calc_dqt_hash(dqt)) # DB Insert를 위해 type(list -> string)
exif = exiftool(image)

# DB Hash 비교를 통해 사용했을 가능성이 있는 Editor 확인 
cursor_db.execute('SELECT * FROM Editor_DQT')
raw_data = cursor_db.fetchall()
Last_Source_Candidate = [] # 'exif(정보가 없는 경우)와 DQT'가 같은 editor 후보군

for r in raw_data:
    if exif == r[1] and hash == r[2]:
        Last_Source_Candidate.append(r[0])

if len(Last_Source_Candidate) == 0:
    print('\033[31m' + "The Last Source is Unknown." + '\033[0m')
elif len(Last_Source_Candidate) == 1:
    if exif.strip() != '': # exif에 정보가 있고, DQT가 같을 경우
        print("Last source of '{}' : ".format(image), end='')
        print('\033[31m' + Last_Source_Candidate[0] + '\033[0m')
    else: # exif에 정보가 없고, DQT만 같을 경우
        print("Last source Candidate of '{}' : ".format(image), end='')  
        print('\033[31m' + Last_Source_Candidate[0] + '\033[0m')
else: # len(Last_Source_Candidate) >= 2 일 경우, Input_image_filename에 Editor 특징을 갖고 있는지 확인 
    cursor_db.execute('SELECT * FROM Editor_Filename')
    filename_data = cursor_db.fetchall()
    input_image_filename = image.split("\\")[-1]
    
    # editor명과, filename특징이 있을 경우 LS 
    check = 0
    for c in Last_Source_Candidate:
        for f in filename_data:
            if (c == f[0]) and (f[1] in input_image_filename):
                print("Last source of '{}' : ".format(image), end='')
                print('\033[31m' + c + '\033[0m')
                check += 1
    
    # Editor_Filename 자체에 특정 editor가 없을 경우, 다른 LSC의 특징에 맞지 않는 LSC는 remove
    if check == 0:
        
        count = len(Last_Source_Candidate)
        idx = 0
        for i in range(count):
            for f in filename_data:
                if (Last_Source_Candidate[idx] == f[0]) and (f[1] not in input_image_filename):
                    Last_Source_Candidate.remove(f[0])
                    if len(Last_Source_Candidate) < 1:
                        break 
                    idx-=1
            if len(Last_Source_Candidate) < 1:
                break
            else:
                idx+=1

        if len(Last_Source_Candidate) >= 1:
            for c in Last_Source_Candidate: 
                print("Last source of '{}' : ".format(image), end='')
                print('\033[31m' + c + '\033[0m')
        else:
            print('\033[31m' + "The Last Source is Unknown." + '\033[0m')

connect_db.close()
