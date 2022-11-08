import flask
import wavfile
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'wavs'
ALLOWED_EXTENSIONS = {'wav'}

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 # limit requests to 1MB


# Build a simple API server to handle user audio projects.
# Your server should provide endpoints that allow a user to perform the following actions: 

# 1. POST raw audio data and store it. 
    # Eg: $ curl -X POST --data-binary @myfile.wav 
    # http://localhost/post 

# 2. GET a list of stored files, GET the content of stored files, and GET metadata of stored files, such as the duration of the audio.
# The GET endpoint(s) should accept a query parameter that allows the user to filter results. Results should be returned as JSON. 
    # Eg: $ curl http://localhost/download?name=myfile.wav 
    # Eg: $ curl http://localhost/list?maxduration=300 
    # Eg: $ curl http://localhost/info?name=myfile.wav 


@app.route('/upload/', methods=["POST"])
def upload_file():
    uploaded_file = flask.request.files['file']
    filename = uploaded_file.filename

    if not allowed_file(filename):
        return invalid_filename_error()

    filename = secure_filename(filename)

    cwd = os.getcwd()
    uploaded_file.save(os.path.join(cwd, UPLOAD_FOLDER, filename))

    response = {
        "filename": filename,
    }
    response = flask.jsonify(**response)
    response.status_code = 200
    return response


@app.route('/list/', methods=["GET"])
def get_list():
    maxDuration = flask.request.args.get('maxduration', default=float('inf'), type=float)

    files = []
    cwd = os.getcwd()
    for filename in os.listdir(os.path.join(cwd, UPLOAD_FOLDER)):
        if allowed_file(filename):
            wavf = wavfile.open(os.path.join(cwd, UPLOAD_FOLDER, filename), 'r')
            if (wavf.duration <= maxDuration):
                files.append(filename)

    response = {
        "files": files,
    }

    return flask.jsonify(**response)

@app.route('/info/', methods=["GET"])
def get_info():
    filename = flask.request.args.get('name', default="", type=str)
    if filename == "":
        return no_filename_error()

    if not allowed_file(filename):
        return invalid_filename_error()

    cwd = os.getcwd()
    filepath = os.path.join(cwd, UPLOAD_FOLDER, filename)
    wavf = wavfile.open(filepath, 'r')

    response = {
        "duration": wavf.duration,
        "num_channels": wavf.num_channels,
        "sample_rate": wavf.sample_rate,
        "metadata": wavf.metadata,
    }
    return flask.jsonify(**response)

@app.route('/download/', methods=["GET"])
def get_file():
    filename = flask.request.args.get('name', default="", type=str)
    if filename == "":
        return no_filename_error()

    if not allowed_file(filename):
        return invalid_filename_error()

    cwd = os.getcwd()
    upload_dir = os.path.join(cwd, UPLOAD_FOLDER)
    return flask.send_from_directory(upload_dir, filename, as_attachment=True)


def no_filename_error():
    error = {
    "message": "Please specify file name!",
    "status_code": 400
    }
    response = flask.jsonify(**error)
    response.status_code = 400
    return response

def invalid_filename_error():
    error = {
    "message": "Invalid file name!",
    "status_code": 400
    }
    response = flask.jsonify(**error)
    response.status_code = 400
    return response

# verifies that filename is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
