# Import libraries
import face_recognition
import pickle
import cv2
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Menginisialisasi koneksi ke database di Google Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-edd47-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "faceattendancerealtime-edd47.appspot.com"
})

# Import image dari folder laptop
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = [] # List untuk setiap gambar
studentIds = [] # List untuk nama file/id gambar
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0]) # Menghilangkan .png pada nama file dan memasukkannya dalam list studentIds
    
    # Mengambil gambar dari folder laptop dan menguploadnya ke database
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
print(studentIds)

# Melakukan encoding pada setiap gambar/wajah
def findEncodings(imagesList):
    encodeList = [] # List untuk semua hasil encoding
    for img in imagesList:
        # Library opencv menggunakan BGR, tetapi library face_recognition menggunakan RGB, maka harus dikonversi dari BGR ke RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList) # The 128 measurements for each face.
encodeListKnownWithIds = [encodeListKnown, studentIds] # Data yang ingin disimpan ke dalam EncodeFile.p (encodeLIstKnown dan studentIds)
print("Encoding Complete")

# Menyimpan data hasil encoding ke dalam file EncodeFile.p
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")