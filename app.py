from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "테스트얌"

if __name__ == "__main__":
    app.run(debug=True)
