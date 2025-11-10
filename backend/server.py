from flask import Flask, jsonify, request
import json, os, time, random, string

app = Flask(__name__)

KEY_FILE = "keys.txt"
LOG_FILE = "log.txt"

def load_keys():
    if not os.path.exists(KEY_FILE):
        return []
    with open(KEY_FILE, "r") as f:
        return json.load(f)

def save_keys(keys):
    with open(KEY_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def log_action(text):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")

def generate_key():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=28))
    return "MIYU-" + random_part

@app.route("/api/create")
def create_key():
    hours = int(request.args.get("hours", 24))
    expiry = int(time.time() + hours * 3600)
    new_key = generate_key()

    keys = load_keys()
    keys = [k for k in keys if k["expiry"] > time.time()]
    keys.append({"key": new_key, "expiry": expiry})
    save_keys(keys)

    log_action(f"Tạo key mới: {new_key}, {hours}h")
    return jsonify({"status": "ok", "key": new_key})

@app.route("/api/list")
def list_keys():
    keys = load_keys()
    now = time.time()
    active = []
    for k in keys:
        if k["expiry"] > now:
            remaining = int((k["expiry"] - now) / 3600)
            active.append({"key": k["key"], "remaining": f"{remaining}h"})
    save_keys([k for k in keys if k["expiry"] > now])
    return jsonify(active)

@app.route("/api/check")
def check_key():
    key = request.args.get("key", "")
    keys = load_keys()
    now = time.time()
    for k in keys:
        if k["key"] == key:
            if k["expiry"] > now:
                remaining = int((k["expiry"] - now) / 3600)
                return jsonify({"valid": True, "remaining": f"{remaining}h"})
            else:
                return jsonify({"valid": False, "reason": "Key hết hạn"})
    return jsonify({"valid": False, "reason": "Không tồn tại"})

@app.route("/")
def home():
    return "MIYU Key Server đang hoạt động"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
