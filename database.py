import json

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
            print(type(json1[i]))
            if not(type(json1[i]) == list):
                json1[i] = json2[i]
            else:
                json1[i].append(json2[i])
    return json1

def contains_id(json_list, id):
    for i in json_list:
        if i["id"] == id:
            return json_list.index(i)
    return None

def read_db():
    with open("./database/db.json", "r") as jsonFile:
        data = json.load(jsonFile)
    return data

def write_db(old_data):
    with open("./database/db.json", "w") as jsonFile:
        json.dump(old_data, jsonFile)