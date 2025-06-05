from app import create_app,render_template,current_app
from os import system,getenv
# system("clear")
from dotenv import load_dotenv
import logging

DEBUG = getenv("DEBUG", True)== "true"
HOST = getenv("HOST", "0.0.0.0")
PORT = getenv("PORT", 5000)

# Load environment variables from .env if present
load_dotenv()

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__': 
    app.run(debug=DEBUG,threaded=True, host=HOST,port=PORT)
