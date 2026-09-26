from flask import Flask, Response, render_template, request
from camera import generate_frames

user = "not logged in"
guser_score = 0

app = Flask(__name__, template_folder=".")
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', user=user)

@app.route('/result', methods=['POST', 'GET'])
def result():
    global user, guser_score
    signed = request.form.get("name")
    password = request.form.get("password")
    logs = list(open("logins.txt", "r").read().splitlines())
    users = list(logs[0].split(","))
    passwords = list(logs[1].split(","))
    score = list(logs[2].split(","))
    if signed in users:
        if password == passwords[users.index(signed)]:
            user = signed
    else:
        signup = open("logins.txt", "w")
        logs[0] = logs[0] + "," + signed
        logs[1] = logs[1] + "," + password
        logs[2] = logs[2] + "," + "0"
        signup.write("\n".join(logs) + "\n")
        signup.close()
        user = signed
    try:
        user_score = score[users.index(user)]
    except:
        user_score = "0"

    debugscore = ""
    for i in user_score:
        if i.isnumeric():
            debugscore += i
    guser_score = int(debugscore)
    return render_template('index.html', user=user, score=str(guser_score))

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    global guser_score
    if user != "not logged in":
        return render_template('index.html', user=user, score=str(guser_score))
    return render_template('index.html', user=user)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global user
    user = "not logged in"
    return render_template('index.html', user=user)

@app.route('/video_feed')
def video_feed():
    if user != "not logged in":
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

@app.route('/rewards', methods=['GET', 'POST'])

def rewards():
    global guser_score
    if user != "not logged in":
        return render_template('index.html', user=user, score=str(guser_score))
    return render_template('index.html', user=user)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
