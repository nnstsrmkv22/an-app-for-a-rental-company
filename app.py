import re
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory
from database import does_user_exist, compare_json, contains_id, read_db, write_db

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('auth.html', menu="login")

@app.route('/login')
def login():
    return render_template('auth.html', menu="login")

@app.route('/registration')
def registration():
    return render_template('auth.html', menu="registration")

@app.route('/prices')
def price_page():
     return render_template('cardlist.html', main="maincontent")

@app.route('/prices/<car>')
def car_page(car):
     return render_template('car.html', main=car)

@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)

@app.route('/user_login', methods=['post'])
def login_user_req():
    data = request.get_json()

    if(len(data["email"]) == 0):
        return {"message":"Введите почту","code":400}
    if(len(data["password"]) == 0):
        return {"message":"Введите пароль","code":400}

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
        else:
            return {"message":"Был введён неверный пароль ","code":400}

    return {"message": "Указанного пользователя не существует","code":403}

@app.route('/user_registration', methods=['post'])
def registration_user_req():
    email_regex = re.compile((r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"))
    data = request.get_json()

    if(len(data["email"]) == 0):
        return {"message":"Введите почту","code":400}
    if(len(data["password"]) == 0):
        return {"message":"Введите пароль","code":400}
    if len(data["password"]) < 4 or len(data["password"]) > 16:
        return {"message":"Пароль должен быть от 4 до 16 символов","code":400}
    if not(email_regex.fullmatch(data["email"])):
        return {"message":"Почта не подходит по формату: mail@mail.ru","code":400}

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

    return {"message": "Указанный пользователь уже существует","code":403}

@app.route('/car', methods=['GET'])
def get_cars_req():
    data = read_db()
    return data["cars"]

@app.route('/car/<carid>', methods=['GET'])
def get_car_req(carid):
    data = read_db()
    res = {"message":"empty", "code":404}
    for i in data["cars"]:
        if i["id"] == int(carid):
            res = i
    return res

@app.route('/car', methods=["PUT"])
def update_car_req():
    data = request.get_json()
    old_data = read_db()

    cars_list = old_data["cars"]
    
    indexInsideList = contains_id(cars_list,int(data["id"]))
    if indexInsideList:
        start_day = data["avaible_time"][1].split('-')
        end_day = data["avaible_time"][2].split('-')

        if not(len(start_day) == 3 and len(end_day) == 3) :
            return {'message': "Даты не должны быть пустыми", "code":400}

        start_day_datetime = datetime(int(start_day[0]), int(start_day[1]), int(start_day[2]))
        end_day_datetime = datetime(int(end_day[0]), int(end_day[1]), int(end_day[2]))

        if start_day_datetime > end_day_datetime:
            return {'message': "Начало аренды не должно быть позже конца", "code":400}

        isValidStart = datetime.today() > start_day_datetime
        isValidEnd = datetime.today() > end_day_datetime
        if isValidStart or isValidEnd:
            return {'message': "Значение дат не должно быть ниже нынешнего дня", "code":400}

        time_list = cars_list[indexInsideList]["avaible_time"]

        for time in time_list:
            date1 = time[1].split('-')
            date2 = time[2].split('-')
            date_start = datetime(int(date1[0]),int(date1[1]),int(date1[2]))
            date_end = datetime(int(date2[0]),int(date2[1]),int(date2[2]))
            if (date_start <= start_day_datetime and date_end >= start_day_datetime) or (date_start <= end_day_datetime and date_end >= end_day_datetime):
                return {'message': "Значение дат находится между другими датами", "code":400}
            if (date_start >= start_day_datetime and date_end <= end_day_datetime):
                return {'message': "Значение дат включает даты чужой аренды", "code":400}
        cars_list[indexInsideList] = compare_json(cars_list[indexInsideList], data)
    else:
        return {'message': "Id товара не существует в базе данных","code":400}

    old_data["cars"] = cars_list

    write_db(old_data)

    return old_data

if __name__ == "__main__":
    app.run(debug=True)