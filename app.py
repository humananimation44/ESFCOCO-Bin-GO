from flask import Flask, Response, render_template, request
from camera import generate_frames
app = Flask(__name__, template_folder=".")
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    name = request.form.get("name")
    return render_template('index.html', name=name)

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    return render_template('demo.html')

@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)