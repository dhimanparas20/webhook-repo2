from app import create_app,render_template
from os import system
system("clear")

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__': 
    app.run(debug=True,threaded=True, host="0.0.0.0",port=5000)
