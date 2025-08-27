from flask import Flask, jsonify, render_template, Response, session, redirect, url_for, request, send_from_directory
import json
from dotenv import load_dotenv
import time
import paho.mqtt.client as mqtt
import os
from threading import Thread
import ssl
import uuid
from queue import Queue, Empty
import requests
import ssl
from ftplib import FTP_TLS
from io import BytesIO

# Gunicorn Single Worker 5 Threads

# Import Environment Variables
load_dotenv()
IP = os.getenv("IP")
CONTROLLER_IP = os.getenv("CONTROLLER_IP")
ACCESS_CODE = os.getenv("ACCESS_CODE")
SERIAL = os.getenv("SERIAL")
TOPIC = f"device/{SERIAL}/report"

# Initialize App Variables
app = Flask(__name__)
app.secret_key = "topsecret"
printer_status = {}
q = Queue()
cl=None
latest_frame = None

# Dedicate Threading Worker
def launch_threads():
    Thread(target=launch_queue, daemon=True).start()
    Thread(target=pull_stream, daemon=True).start()

# Constructs MJPEG Stream
def pull_stream():
    global latest_frame
    url=f"http://127.0.0.1:1984/api/stream.mjpeg?src=bambu_camera"
    go=False
    while True:
        try:
            with requests.get(url, stream=True, timeout=10) as r:
                fine=r.raise_for_status()
                if fine==None:
                    go=True
                    buf = b""
                    for chunk in r.iter_content(chunk_size=4096):
                        if go:
                            print("Camera Connected")
                            go=False
                        if not chunk:
                            continue
                        buf += chunk
                        # Look for JPEG start & end markers
                        start = buf.find(b'\xff\xd8')  # SOI
                        end = buf.find(b'\xff\xd9', start + 2)  # EOI
                        if start != -1 and end != -1:
                            jpg = buf[start:end + 2]
                            buf = buf[end + 2:]
                            latest_frame = jpg
        except Exception as e:
            print(f"Camera Disconnected. {e}: Reconnecting...")
            go=False
            continue

# Runs On MQTT Connection
def on_connect(client, userdata, flags, rc):
    global printer_status
    if rc == 0:
        printer_status.update({"connection": True})
        print("MQTT Connection Established")
        client.subscribe(TOPIC, qos=0)
    else:
        print("MQTT Connection Failed:", rc)

# Runs After MQTT Updates
def on_message(client, userdata, msg):
    global printer_status
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        printer_status.update(data)
    except Exception as e:
        print("Payload Error:", e)

# Runs On MQTT Disconnect
def on_disconnect(client, userdata, rc):
    global printer_status
    printer_status.update({"connection": False})
    print("MQTT Disconnected:", rc)

# Establish MQTT Client Connection
def connect():
    global cl
    cl_id = f"lan-402438-{uuid.uuid4().hex[:6]}"
    cl = mqtt.Client(client_id=cl_id, clean_session=True, protocol=mqtt.MQTTv311)
    print("Connecting...")
    cl.username_pw_set("bblp", ACCESS_CODE)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_verify_locations(cafile="static/blcert.pem")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    cl.tls_set_context(ctx)
    cl.tls_insecure_set(True)
    cl.on_connect = on_connect
    cl.on_message = on_message
    cl.on_disconnect = on_disconnect
    cl.reconnect_delay_set(min_delay=1, max_delay=60)
    cl.connect_async(IP, 8883, keepalive=120)
    cl.loop_start()

# Launch Background Queue
def launch_queue():
    global printer_status
    printer_status = {"connection": False}
    time.sleep(1) 
    connect()
    time.sleep(5)
    try:
        while True:
            try:
                item = q.get(timeout=1)

                q.task_done()
            except Empty:
                if printer_status.get("connection")==False:
                    pass
    except Exception as e:
        print("Queue Error:", e)

# POST File to FTPS Server
def upload_file(file, name):
    try:
        name=name.replace(".3mf", "")
        ctx = ssl.create_default_context(cafile="ca_cert.pem")
        ftps = FTP_TLS(context=ctx)
        ftps.connect(IP, 990, timeout=10)
        ftps.prot_p()
        ftps.login(user="bblp", passwd=ACCESS_CODE)
        ftps.set_pasv(True)
        with BytesIO(file) as buf:
            buf.seek(0)
            ftps.storbinary(f"STOR /mnt/sdcard/{name}.3mf", buf, blocksize=256*1024) # change path
        ftps.quit()
        return True
    except Exception as e:
        print("FTPS Upload Error:", e)
        return False
    finally:
        ftps.quit()

# Serves Homepage
@app.route("/", methods=["GET"])
def main():
    return render_template("main.html")

# Serves JSON Printer Status
@app.route("/update", methods=["GET"])
def update():
    status = printer_status
    if isinstance(status, dict):
        return jsonify(status)
    if isinstance(status, (str, bytes)):
        return Response(status, mimetype="application/json")
    return jsonify({"error": "empty"}), 404

# Serves MJPEG Stream
@app.get("/mjpeg")
def mjpeg():
    boundary = "frame"
    def gen():
        while True:
            if latest_frame:
                yield (b"--" + boundary.encode() + b"\r\n"
                       b"Content-Type: image/jpeg\r\n"
                       b"Cache-Control: no-store\r\n\r\n" +
                       latest_frame + b"\r\n")
            time.sleep(0.05)
    return Response(gen(), mimetype=f"multipart/x-mixed-replace; boundary={boundary}")

# Receives File Uploads
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    if ".3mf" not in file.filename:
        return "OK", 409
    print(file.filename) 
    data=file.read()
    status=upload_file(data, file.filename)
    if status==False:
        return "OK", 409
    return "OK", 200

# Launch App
if __name__ == '__main__':
    launch_threads()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
