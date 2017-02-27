from flask import Flask, request
import waitress
from requestlogger import WSGILogger, ApacheFormatter
import logging
import sys
import operations


operator = operations.TVOperator(debug=False)
app = Flask("tvcontrol")

@app.route("/tvcontrol", methods=["POST"])
def tvcontrol():
    action = request.form['action']
    channel = int(request.form['channel'])

    if action == "watch_channel":
        operator.watch_channel(channel)
    elif action == "watch_cbeebies":
        operator.watch_channel(124)
    elif action == "watch_tv":
        operator.watch_tv()
    elif action == "watch_bd":
        operator.watch_bd()
    elif action == "turn_off":
        operator.all_off()
    elif action == "watch_fire":
        operator.watch_fire()
    return "OK\n"
    

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    loggingapp = WSGILogger(app, [ch], ApacheFormatter())
    waitress.serve(loggingapp, host='0.0.0.0', port=1025)

