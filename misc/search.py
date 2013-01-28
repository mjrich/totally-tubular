from flask import Flask
from flask import render_template
from flask import request
import gdata.youtube.service

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True

app = Flask(__name__)


@app.route('/search', methods = ['GET', 'POST'])
def search():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(debug=True)
