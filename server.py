from flask import Flask, render_template, Response
from picamera import PiCamera
from time import sleep
import io

app = Flask(__name__)

def gen(camera):
    """Video streaming generator function."""
    while True:
        stream = io.BytesIO()
        camera.capture(stream, 'jpeg', use_video_port=True)
        stream.seek(0)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')
        stream.close()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(PiCamera(resolution='640x480', framerate=24)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
