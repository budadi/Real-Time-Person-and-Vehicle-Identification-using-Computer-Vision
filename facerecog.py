import cv2
import threading
import time
import requests
import base64
import face_recognition
from pymongo import  MongoClient
from datetime import datetime



client = MongoClient('mongodb+srv://varun898080:123@cluster0.1gxfd.mongodb.net/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE')
name=""
phone=""
db=client['test']
collection= db['images']
collection2=db['refs']
print(time.time())
found=0
def getImage():
    for docs in collection2.find():
        global name, phone
        name=docs['Name']
        print(name)
        data = docs['Data']
        d1 = data.split(',')[1]
        decoded_data=base64.b64decode(d1)
        with open('test.jpg','wb') as f:
            f.write(decoded_data)
getImage()


cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("simps.jpg")
#cap = cv2.VideoCapture("rtsp://192.168.62.89:8080/h264_ulaw.sdp")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

reference_img = face_recognition.load_image_file("test.jpg")
reference_encoding = face_recognition.face_encodings(reference_img)[0]

face_match = False
counter = 0
check_frequency = 30
check_face_thread = None



def check_face(img):
    global face_match, check_face_thread

    try:
        face_encodings = face_recognition.face_encodings(img)
        if len(face_encodings) > 0:
            match_results = face_recognition.compare_faces([reference_encoding], face_encodings[0])
            face_match = match_results[0]

            if face_match:
                check_face_thread.cancel()
    except:
        pass

def sendImage():
    dd = "data:image/jpeg;base64"
    try:
        with open('screenshot.jpg','rb') as f:
            data=f.read()
            encoded_data = str(base64.b64encode(data)).split("b'")
            a=dd+","+encoded_data[1]
            a=a[:-1]
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            doc = {'Name': name, 'Data': str(a),'Location':"12.8409/77.5117", 'Time':str(current_time)}
            collection.insert_one(doc)
    except Exception as e:
        print("error",e)


while True:
    start_time = time.time()

    success, img = cap.read()

    if success:

        if counter % check_frequency == 0 and not face_match:
            if face_match:
                print(face_match)
            check_face_thread = threading.Thread(target=check_face, args=(img.copy(),))
            check_face_thread.start()

        counter += 1

        if face_match:
            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)
            face_distances = face_recognition.face_distance(face_encodings, reference_encoding)

            try:
                best_match_index = face_distances.argmin()
                if face_distances[best_match_index] < 0.5:
                    top, right, bottom, left = face_locations[best_match_index]
                    cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(img, "MATCH", (left, top - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.imwrite("screenshot.jpg", img)
                    found=1
                    break
                else:
                    cv2.putText(img, "NO MATCH", (20, 450), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)
            except:
                pass
        else:
            cv2.putText(img, "NO MATCH", (20, 450), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)

    cv2.imshow("video", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

    end_time = time.time()
    elapsed_time = end_time - start_time
    fps = 1 / elapsed_time

    # Display FPS on the video stream
    cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("video", img)
if(found):
    sendImage()
cv2.destroyAllWindows()