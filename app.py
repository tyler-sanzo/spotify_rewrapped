from flask import Flask, render_template, request
app = Flask(__name__)
app.debug = True


@app.route('/', methods=['GET'])
def dropdown():
    timespan = ['Last four weeks', 'Last six months', 'Last five years']
    return render_template('index.html', timespan=timespan)

if __name__ == "__main__":
    app.run()

@app.route("/")
def view_home():
    return render_template("index.html", title="Home page")

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('action1') == 'VALUE1':
            pass # do something
        else:
            pass # unknown
    elif request.method == 'GET':
        return render_template('index.html', form=form)
    
    return render_template("index.html")

@app.route("/first")
def view_first_page():
    return render_template("index.html", title="First page")

@app.route("/second")
def view_second_page():
    return render_template("index.html", title="Second page")