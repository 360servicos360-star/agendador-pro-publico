# app.py
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import jwt, os, uuid, threading, subprocess
from twilio.rest import Client

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

JWT_SECRET = os.environ.get('JWT_SECRET', 'change-me')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/send_record_link', methods=['POST'])
def send_record_link():
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'phone is required'}), 400

    req_id = str(uuid.uuid4())
    token = jwt.encode({'req_id': req_id}, JWT_SECRET, algorithm='HS256')
    link = f"{request.url_root}record?token={token}"

    twilio_sid = os.environ.get('TWILIO_SID')
    twilio_token = os.environ.get('TWILIO_TOKEN')
    twilio_from = os.environ.get('TWILIO_FROM')

    if twilio_sid and twilio_token and twilio_from:
        client = Client(twilio_sid, twilio_token)
        client.messages.create(
            to=phone,
            from_=twilio_from,
            body=f"Gravação biométrica: {link}"
        )

    return jsonify({'link': link, 'token': token, 'req_id': req_id})

@app.route('/record')
def record_page():
    token = request.args.get('token')
    if not token:
        return 'Token inválido', 403
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception:
        return 'Token inválido', 403
    return send_from_directory('static', 'record.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    token = request.form.get('token')
    if not token:
        return jsonify({'error':'token is required'}), 400
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception:
        return jsonify({'error':'invalid token'}), 403

    file = request.files.get('video')
    if not file:
        return jsonify({'error':'video file is required'}), 400

    filename = secure_filename(file.filename) or 'video.webm'
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return jsonify({'status':'ok', 'path': path})

@app.route('/schedule', methods=['POST'])
def schedule():
    payload = request.get_json(silent=True) or {}
    threading.Thread(target=run_scheduler, args=(payload,), daemon=True).start()
    return jsonify({'status': 'scheduled'})


def run_scheduler(payload):
    subprocess.run(['python', 'automation/scheduler.py', '--payload', str(payload)])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
