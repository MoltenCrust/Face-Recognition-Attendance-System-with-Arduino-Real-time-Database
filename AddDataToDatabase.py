# Import libraries
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Menginisialisasi koneksi ke database di Google Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-edd47-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "faceattendancerealtime-edd47.appspot.com"
})

# Menambah data ke dalam database
student = db.reference('Students')
actuator = db.reference('Actuator')
sensor = db.reference('Sensor')

student_data = {
    "001":
        {
            "name": "Bill Gates",
            "major": "Software Engineering",
            "starting_year": 2017,
            "total_attendance": 0,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "002":
        {
            "name": "Dwayne Johnson",
            "major": "Math",
            "starting_year": 2021,
            "total_attendance": 0,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "003":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 0,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "004":
        {
            "name": "Fredrik",
            "major": "IBDA",
            "starting_year": 2021,
            "total_attendance": 0,
            "standing": "A",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "005":
        {
            "name": "Yechiel Ardner Arianto",
            "major": "IBDA",
            "starting_year": 2021,
            "total_attendance": 0,
            "standing": "B",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "006":
        {
            "name": "Moses Anthony Kwik",
            "major": "IEE",
            "starting_year": 2021,
            "total_attendance": 0,
            "standing": "C",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}

actuator_data = {
    "11001":
        {
            "type": "rotary actuator",
            "times_triggered": 0
        }
}

sensor_data = {
    "22001":
        {
            "type": "ultrasonic sensor",
            "times_triggered" : 0,
            "distance": 0
        }
}

for key, value in student_data.items():
    student.child(key).set(value)

for key, value in actuator_data.items():
    actuator.child(key).set(value)

for key, value in sensor_data.items():
    sensor.child(key).set(value)