import os
from werkzeug.utils import secure_filename
from flask import Flask, request
import json

app = Flask(__name__)
UPLOAD_FOLDER = './static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/user_login', methods=['post'])
def login_user_req():
    data = request.get_json()
    old_data = read_db()
    user_list = old_data["users"]

    user_existance = does_user_exist(user_list, data["email"])
    if user_existance["exist"]:
        if user_existance["user"]["password"] == data["password"]:
            res = {
                "id": user_existance["user"]["id"],
                "email": user_existance["user"]["email"],
            }
            return res

    return {"message": "Указанного пользователя не существует"}

@app.route('/user_registration', methods=['post'])
def registration_user_req():
    data = request.get_json()
    old_data = read_db()
    user_list = old_data["users"]

    user_existance = does_user_exist(user_list, data["email"])
    if not(user_existance["exist"]):
        last_id = user_list[len(user_list)-1]["id"] + 1
        old_data["users"].append({
            "id":last_id,
            "email": data["email"],
            "password": data["password"]
        })
        res = {
            "id": last_id,
            "email":  data["email"],
        }
        write_db(old_data)
        return res

    return {"message": "Указанный пользователь уже существует"}

@app.route('/car', methods=['GET'])
def get_cars_req():
    data = read_db()
    return data


@app.route('/car', methods=["PUT"])
def update_car_req():
    data = request.get_json()
    old_data = read_db()

    cars_list = old_data["cars"]
    
    indexInsideList = contains_id(cars_list,int(data["id"]))

    if indexInsideList:
        cars_list[indexInsideList] = compare_json(cars_list[indexInsideList], data)
    else:
        return {'message': "Id товара не существует в базе данных"}

    old_data = {"cars":cars_list}

    write_db(old_data)

    return old_data

    
def does_user_exist(user_list, user_email):
    for i in user_list:
        if i["email"] == user_email:
            return {
                "exist": True, 
                "user": i
                }
    return {"exist": False, "user":None}

def compare_json(json1, json2):
    for i in list(json1.keys()):
        if i in json2:
            json1[i] = json2[i]
    return json1

def contains_id(json_list, id):
    for i in json_list:
        if i["id"] == id:
            return json_list.index(i)
    return False

def read_db():
    with open("./database/db.json", "r") as jsonFile:
        data = json.load(jsonFile)
    return data

def write_db(old_data):
    with open("./database/db.json", "w") as jsonFile:
        json.dump(old_data, jsonFile)

if __name__ == "__main__":
    app.run(debug=True)