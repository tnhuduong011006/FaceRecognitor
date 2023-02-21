'''
    Đề tài 06: Xây dựng ứng dụng nhận dạng người nổi tiếng
    Thành viên nhóm:
    Nguyễn Thị Bích Ngọc    B1913323
    Dương Thị Tố Như        B1913327
'''
# Thực hiện các bước face_recognition

import pandas as pd
import requests
import cv2,os
from bs4 import BeautifulSoup
import mysql.connector
import face_recognition

# số mẫu
n = 50

# Connect mysql
mydb = mysql.connector.connect(
  host="localhost",
  user="tnhu",
  password="abc123",
  database="qluser"
)

'''###############Prepare Data############'''
# Hàm cập nhật tên và ID vào CSDL
def insertOrUpdate(id, name, job):

    mycursor = mydb.cursor()
    
    # Thực thi câu lệnh 
    insert_stmt = (
        "SELECT * FROM nguoidung where id = %(n_id)s"
    )
    
    isRecordExist=0
    mycursor.execute(insert_stmt, {'n_id': id})
    
    myresult = mycursor.fetchall()
    for row in myresult:
        isRecordExist = 1
        break     

    if isRecordExist==1:
        cmd = ("UPDATE nguoidung SET hoten = %(name)s, job = %(job)s  WHERE id= %(n_id)s")
    else:
        cmd="INSERT INTO nguoidung(id,hoten,job) Values(%(n_id)s, %(name)s, %(job)s)"

    mycursor.execute(cmd, {'n_id': id, 'name': name, 'job': job})
    mydb.commit() # Lệnh để apply thay đổi

data = pd.read_csv('https://raw.githubusercontent.com/tnhuduong011006/faceRe/master/Famous%20Personalities.csv')
name = data["name"]
job = data["known_for_department"]

list = {}

idx = "10000"
stt = -1
for i in range(len(name)):
    stt += 1
    if stt == n:
        break
    id = str(int(idx) + stt)
    id = id[-4:]
    list.update({id : {"hoten" : name[i], "job" : job[i]}})
    # Đưa thông tin người vào csdl
    insertOrUpdate(id,name[i], job[i])

root = os.getcwd()

'''*****************Dự đoán********************'''
id=0
#set text style
fontface = cv2.FONT_HERSHEY_SIMPLEX
fontscale = 0.5
fontcolor = (0,255,0)
fontcolor1 = (0,0,255)

# Hàm lấy thông tin người dùng qua ID
def getProfile(id):

    mycursor = mydb.cursor()
    
    # Thực thi câu lệnh 
    insert_stmt = (
        "SELECT * FROM nguoidung where id = %(n_id)s"
    )
    
    mycursor.execute(insert_stmt, {'n_id': id})
    myresult = mycursor.fetchall()
    profile=None
    for row in myresult:
        profile=row

    return profile


# tạo encodelist ảnh của đối tượng đưa vào dict
dictImg = dict()
crawlp = os.path.join(root,"crawlPicture")
for i in list:
    # Trỏ đến thư mục mong muốn
    path = os.path.join(crawlp,i)

    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 

    sampleNum=0
    listEncodeImg = []
    
    for imgpath in imagePaths:
        try:
            img = face_recognition.load_image_file(imgpath)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            listEncodeImg.append(encode)
        except:
            pass
    
    dictImg.update({i:listEncodeImg})

'''################## Face Recognizer #################'''
import cv2
import face_recognition


from flask import Flask,render_template,Response
import cv2

app=Flask(__name__)
cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        print(facesCurFrame, "\n")
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
        listFaceDis= [] #Chứa khoảng cách
        listMatches = []
        for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
            for i in dictImg:
                faceDis = face_recognition.face_distance(dictImg[i], encodeFace)
                matches = face_recognition.compare_faces(dictImg[i], encodeFace)
                try:
                    listFaceDis.append(min(faceDis))
                    for j in range(len(faceDis)):
                        if faceDis[j] == min(faceDis):
                            break
                    listMatches.append(matches[j])
                except:
                    listFaceDis.append(1)
                    listMatches.append("False")
        
            name = 'Unknown'
            job = "Unknown"
            index = listFaceDis.index(min(listFaceDis))
            try:
                if listFaceDis[index] <= 0.45:
                        
                    idx = '10000'
                    id = str(int(idx) + index)
                    id = id[-4:]
                            
                    profile = getProfile(id)
                    name = str(profile[1])
                    job = str(profile[2])
                    
            except:
                pass
            
            name = "Name: " + name
            job = "Job: " + job
            print(name)

            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2),(x2,y2+60),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2+22),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
            cv2.putText(img,job,(x1+6,y2+50),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
        cv2.imshow("New Face", img)
        cv2.waitKey(1)

generate_frames()        
# =============================================================================
#             ret,buffer=cv2.imencode('.jpg',img)
#             img=buffer.tobytes()
#     
#             yield(b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
# 
# 
# @app.route('/')
# def index():
#     return render_template('index.html')
# 
# @app.route('/video')
# def video():
#     return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')
# 
# if __name__=="__main__":
#     app.run(debug=True)
# =============================================================================
