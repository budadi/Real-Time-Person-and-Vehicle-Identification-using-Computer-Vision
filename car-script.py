import cv2
import pytesseract
import re
import time
from difflib import SequenceMatcher
from pymongo import MongoClient
from datetime import datetime
import  base64
import pywhatkit



def match_percentage(str1, str2):
    matcher = SequenceMatcher(None, str1, str2)
    return round(matcher.ratio() * 100, 2)


# def whatsappmsg(str):
#     Mobile_NO="+91 9480463783"
#     image_path =r"FOUND.jpg"
#     caption =str
#     current_time = datetime.now()
#     time_plus_5_minutes = current_time + datetime.timedelta(seconds=18)

#     wait_time = int((time_plus_5_minutes - datetime.datetime.now() - datetime.timedelta(seconds=7)).total_seconds())+2

#     pywhatkit.sendwhats_image(Mobile_NO, image_path, caption, wait_time,True)


harcascade = "haarcascade_russian_plate_number.xml"
url1 = "rtsp://192.168.6.152:8080/h264_ulaw.sdp"

client = MongoClient('mongodb+srv://shreyas:shreyas@cluster0.7sqc1vd.mongodb.net/?retryWrites=true&w=majority')
# name = ""
tempdata = ["HR26DK8337"]
db = client['test']
collection = db['plates']
collection2=db['platedatas']
print(collection)
for docs in collection.find():
    if (docs['number'] not in tempdata):
        tempdata.append(docs['number'])
        # name=docs['number']
print(tempdata)

def sendImage(name):
    dd = "data:image/jpeg;base64"
    try:
        with open('FOUND.jpg','rb') as f:
            data=f.read()
            encoded_data = str(base64.b64encode(data)).split("b'")
            a=dd+","+encoded_data[1]
            a=a[:-1]
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            doc = {'Name': name, 'Data': str(a),'Location':" 12.8794/77.5443", 'Time':str(current_time)}
            collection2.insert_one(doc)
            print(collection2)
    except Exception as e:
        print("error",e)

cap = cv2.VideoCapture(0)

min_area = 500
count = 0
a = 1

while True:
    success, img = cap.read()
    cv2.imshow('img', img)

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Match", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
            cv2.imwrite("FOUND.jpg", img)

            img_roi = img[y:y + h, x:x + w]
            cv2.imwrite("saved.jpg", img_roi)

            crop_img_loc = "saved.jpg"

            start_time = time.time()
            text = pytesseract.image_to_string(crop_img_loc, lang='eng')
            end_time = time.time()

            if text != "":

                for i in tempdata:
                    if (match_percentage(i, text)) > 60:
                        print("Match Found=>" + i)
                        sendImage(i)
                        # whatsappmsg(i)
                        exit(0)
                    else:
                        print("Searching...")
            else:
                print("Searching...")

            if cv2.waitKey(1) == ord("q"):
                break

cap.release()
cv2.destroyAllWindows()