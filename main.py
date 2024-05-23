# Install dan import library: cmake, dlib, face-recognition, cvzone, opencv-python, firebase-admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from datetime import datetime
from pymata4 import pymata4
import face_recognition
from time import sleep
import firebase_admin
import numpy as np
import cvzone
import pickle
import time
import cv2
import os

# Menginsialisasi koneksi ke database di Google Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-edd47-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "faceattendancerealtime-edd47.appspot.com"
})
bucket = storage.bucket()

# 1366 x 768
# database img 216x216

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources1/background.png')

# Importing the mode images into a list
folderModePath = 'Resources1/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))


# Arduino Servo
board = pymata4.Pymata4()
port = "COM7"
pos = 0

def servo(my_board, pin):
    # set the pin mode
    my_board.set_pin_mode_servo(pin)
    my_board.servo_write(pin, pos)
    time.sleep(0.1)

# Arduino Ultrasonic Sensor
import time
triggerPin = 12
echo_pin = 11
board.set_pin_mode_sonar(triggerPin, echo_pin)


# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()    
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

# deklarasi variabel yang diperlukan untuk setiap kondisi dalam while True dibawah
modeType = 0
counter = 0
id = -1
imgStudent = []
actuator_status = 'Closed' # Set string awal status pintu tertutup

red_text = (0, 0, 255)
green_text = (0, 255, 0)
actuator_text_color = red_text

# Memanggil data informasi dari database
actuatorInfo = db.reference(f'Actuator/11001').get()
refActuator = db.reference(f'Actuator/11001')

sensorInfo = db.reference(f'Sensor/22001').get()
refSensor = db.reference(f'Sensor/22001')

while True:
    read = board.sonar_read(triggerPin)
    ultrasonic_value = read[0]
    # tambahkan nilai ultrasonic yang didapatkan ke database
    sensorInfo['distance'] = ultrasonic_value
    refSensor.child('distance').set(sensorInfo['distance'])
    
    # menampilkan status jarak ultrasonic di User Interface
    current_status_ultrasonic = cv2.rectangle(imgBackground, (500, 660), (600, 700), (255, 255, 255), -1)
    current_status_ultrasonic = cv2.putText(imgBackground, str(ultrasonic_value), (500, 700),
                                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
    # menampilkan status aktuator di User Interface
    current_status_actuator = cv2.rectangle(imgBackground, (140, 660), (270, 720), (255, 255, 255), -1)
    current_status_actuator = cv2.putText(imgBackground, actuator_status, (140, 700),
                                            cv2.FONT_HERSHEY_COMPLEX, 1, actuator_text_color, 2)

    # Ultrasonic Sensor1
    # jika jarak yang diterima ultrasonic kurang dari atau sama dengan 5, maka aktuator akan bergerak (kunci terbuka)
    if read[0] <= 5:
        sensorInfo['times_triggered'] += 1
        refSensor.child('times_triggered').set(sensorInfo['times_triggered'])
        actuator_status = 'Opened'
        actuator_text_color = green_text
        pos=180
        servo(board, 10)
        sleep(5)
    # jika jarak yang diterima ultrasonic lebih dari 5, maka aktuator tidak akan bergerak
    elif read[0] > 5:
        actuator_status = 'Closed'
        actuator_text_color = red_text
        pos=0
        servo(board, 10)
        sleep(0.1)
    
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    
    # jika kamera mendeteksi wajah
    if faceCurFrame:
        # mencocokkan wajah yang di scan dengan data yang ada dalam database satu per satu
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)
            # jika ditemukkan wajah yang cocok dengan yang ada di database, akan diproses untuk menampilkan tampilan yang sesuai dengan data user
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

                # status aktuator ditambahkan ke database
                actuatorInfo['times_triggered'] += 1
                refActuator.child('times_triggered').set(actuatorInfo['times_triggered'])

                actuator_status = 'Opened'
                actuator_text_color = green_text
                pos=180
                servo(board, 10)
                sleep(5)
                pos=0
                actuator_text_color = red_text
                actuator_status = 'Closed'
                servo(board, 10)

        # setiap perubahan value counter akan masuk ke kondisi ini
        if counter != 0:
            # jika wajah sudah terdeteksi akan masuk ke kondisi ini
            if counter == 1:
                # Ambil data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Ambil image dari storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                # Update attendance jika sudah lebih dari 30 detik setelah wajah yang sama terdeteksi
                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                # jika belum lebih dari 30 detik dan wajah yang sama terdeteksi masuk ke kondisi ini
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            # ini adalah kondisi dimana wajah yang sama terdeteksi belum lebih dari 30 detik tidak terjadi
            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                # akan muncul tampilan data pemilik wajah di User Interface
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1
                # jika sudah beberapa waktu setelah wajah yang dikenali terdeteksi, akan kembali ke tampilan normal sebelum kamera mendeteksi wajah siapapun.
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    # jika kamera tidak mendeteksi wajah
    else:
        modeType = 0
        counter = 0
        
    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)  