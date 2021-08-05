import flask
from flask import send_from_directory, Flask

app = Flask(__name__)

# The absolute path of the directory containing images for users to download
app.config["filename"] = "F:\\Download\\"


@app.route('/get-file/<filename>', methods=['GET', 'POST'])
def get_file(filename):
    return send_from_directory(app.config["filename"], filename=filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='192.168.0.115', port=8000, debug=True, threaded=True)
