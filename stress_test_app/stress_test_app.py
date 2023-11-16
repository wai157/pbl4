from flask import Flask, render_template
import time

app = Flask(__name__, template_folder='.')

counter = 0
start_time = time.time()

@app.route('/')
def index():
    global counter
    global start_time
    counter += 1
    current_time = time.time()
    return render_template('stress_test_app.html', 
                           counter=counter, 
                           rps=counter/(current_time-start_time), 
                           start_time=time.ctime(start_time), 
                           current_time=time.ctime(current_time))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)