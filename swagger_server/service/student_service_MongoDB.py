import json
import logging
import os
import tempfile

from functools import reduce
import uuid

import pymongo  # package for working with MongoDB

from swagger_server.models import Student

db_dir_path = tempfile.gettempdir()
db_file_path = os.path.join(db_dir_path, "students.json")

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["studentsdb"]
student_db = db["students"]

with open(db_file_path) as f:
    file_data = json.load(f)

student_db.insert(file_data)


def add_student(student):
    if student.first_name is None or student.last_name is None:
        return 'invalid input', 405

    res = student_db.find({"first_name": student.first_name, "last_name": student.last_name})
    if res:
        return 'already exists', 409

    doc_id = student_db.insertOne(student.to_dict())
    student.student_id = doc_id
    return student.student_id, 200


def get_student_by_id(student_id, subject):
    student = student_db.find({"doc_id":int(student_id)})
    if student.count() == 0:
        return "Not Found", 404

    student = Student.from_dict(student)

    if not subject or subject in student.grades:
        return student, 200
    else:
        return 'Not found', 404


def get_student_by_last_name(last_name):
    student = student_db.find({"last_name": last_name})

    if student.count() == 0:
        return "Not Found", 404

    student = Student.from_dict(student)
    return student, 200


def delete_student(student_id):
    student = student_db.find({"doc_id":int(student_id)})
    if student.count() == 0:
        return "Not Found", 404
    student.db.remove({"doc_id":int(student_id)})
    return student_id, 200
