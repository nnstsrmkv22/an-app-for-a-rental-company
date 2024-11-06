import re
from werkzeug.utils import secure_filename
from flask import Flask, request,render_template
from database import does_user_exist, compare_json, contains_id, read_db, write_db

app = Flask(__name__)
UPLOAD_FOLDER = './static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def start():
    return render_template('auth.html', menu="login")

@app.route('/login')
def login():
    return render_template('auth.html', menu="login")
@app.route('/registration')
def registration():
    return render_template('auth.html', menu="registration")

@app.route('/main')
def main_page():
     return render_template('main.html')


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
            return {"message":"Был введён неверный пароль пароль","code":400}

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

if __name__ == "__main__":
    app.run(debug=True)