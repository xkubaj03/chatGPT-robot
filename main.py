from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Hello, this is a response from the server!"

if __name__ == '__main__':
    app.run(port=5005)
