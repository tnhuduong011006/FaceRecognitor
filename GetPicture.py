'''
    Đề tài 06: Xây dựng ứng dụng nhận dạng người nổi tiếng
    Thành viên nhóm:
    Nguyễn Thị Bích Ngọc    B1913323
    Dương Thị Tố Như        B1913327
'''
# Cào ảnh từ trang web và lưu vào các thư mục

import pandas as pd
import requests
import os
from bs4 import BeautifulSoup

# Số lượng người trong tập huấn luyện
n = 50

data = pd.read_csv('https://raw.githubusercontent.com/tnhuduong011006/faceRe/master/Famous%20Personalities.csv')
idsearch = data["id"]
name = data["name"]

'''
    Định dạng cấu trúc của url
    Ví dụ: https://www.themoviedb.org/person/224513-Ana-de-Armas/images/profiles
    - id = 224513
    - name = Ana de Armas
'''
fname = []
for i in range(len(name)):
    fname.append(name[i].replace(" ","-"))
    fname[i] = "-" + fname[i]

# Lấy đường dẫn hiện tại
root = os.getcwd()

listurl = {}
lo = "https://www.themoviedb.org/person/"
ve = "/images/profiles"

idx = "10000"
stt = -1
for i in idsearch:
    stt += 1
    if stt == n:
        break
    id = str(int(idx) + stt)
    id = id[-4:]
    url = lo + str(i) + fname[stt] + ve
    listurl.update({id : url})

headers = {
    'Host': 'www.themoviedb.org',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    
}

# Tạo đường dẫn cho thư mục crawlPicture bằng thuộc tính join
crawlp = os.path.join(root,"crawlPicture")
# Tạo thư mục crawlPicture để lưu hình ảnh đã crawl về
os.mkdir(crawlp)

for i in listurl:
    count = 0
    response = requests.get(listurl[i], headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    image_tags = soup.find_all("img")
       
    # Thiết lập đường dẫn
    path = os.path.join(crawlp, i)
    # Tạo thư mục có đường dẫn là path
    os.mkdir(path)   
    # Thay đổi vị trí thư mục làm việc hiện tại
    os.chdir(path)
    
    for counter, image_tag in enumerate(image_tags):
        try:
            image_url = "https://www.themoviedb.org/" + image_tag['src']
            response = requests.get(image_url)
            if response.status_code == 200:
                print(image_url, response.status_code)
                with open(str(counter) + '.jpg', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=128):
                        f.write(chunk)
                count+= 1
            if count == 5:
                break
        except:
            pass
