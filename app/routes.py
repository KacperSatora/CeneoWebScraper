from app import app

@app.route('/')
@app.route('/index')
def index():
    return " Hello Kacper Satora"

@app.route('/name/',defaults={'name': None})
@app.route('/name/<name>')
def name(name=None):
    return f"Hello {name}"