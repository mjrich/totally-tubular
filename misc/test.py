from flask import Flask
from flask import render_template
import gdata.youtube.service

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True

app = Flask(__name__)

@app.route('/search/')
@app.route('/search/<name>')
def search(name=None):
    return render_template('main.html', name=name)

if __name__ == "__main__":
    app.run()
