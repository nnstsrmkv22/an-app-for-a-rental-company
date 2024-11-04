from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_req():
    return "Hello world"

if __name__ == "__main__":
    app.run(debug=True)