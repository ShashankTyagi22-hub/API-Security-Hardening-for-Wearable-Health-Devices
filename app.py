from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import bcrypt
import uuid
import datetime

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "SUPER_SECRET_JWT_KEY"

jwt = JWTManager(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "20 per minute"]
)

# ------------------------------
# DATABASE
# ------------------------------

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT UNIQUE,
        api_key TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        heart_rate INTEGER,
        steps INTEGER,
        temperature REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ------------------------------
# REGISTER USER
# ------------------------------

@app.route("/")
def home():
    return {
        "message": "Wearable Health Security API Running Successfully"
    }

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    username = data["username"]
    password = data["password"]

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, hashed)
        )

        conn.commit()

    except:
        return jsonify({"error": "User exists"}), 400

    finally:
        conn.close()

    return jsonify({"message": "Registration successful"})

# ------------------------------
# LOGIN
# ------------------------------

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data["username"]
    password = data["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    if not result:
        return jsonify({"error": "User not found"}), 404

    stored_password = result[0]

    if bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password
    ):
        token = create_access_token(identity=username)

        return jsonify({
            "token": token
        })

    return jsonify({
        "error": "Invalid credentials"
    }), 401

# ------------------------------
# DEVICE REGISTRATION
# ------------------------------

@app.route("/register-device", methods=["POST"])
@jwt_required()
def register_device():

    device_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO devices(device_id,api_key)
    VALUES(?,?)
    """, (device_id, api_key))

    conn.commit()
    conn.close()

    return jsonify({
        "device_id": device_id,
        "api_key": api_key
    })

# ------------------------------
# VALIDATE DEVICE
# ------------------------------

def validate_device(device_id, api_key):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM devices
    WHERE device_id=? AND api_key=?
    """, (device_id, api_key))

    device = cursor.fetchone()

    conn.close()

    return device is not None

# ------------------------------
# HEALTH DATA API
# ------------------------------

@app.route("/api/health-data", methods=["POST"])
@limiter.limit("10 per minute")
def health_data():

    data = request.json

    device_id = data.get("device_id")
    api_key = data.get("api_key")

    if not validate_device(device_id, api_key):
        return jsonify({
            "error": "Unauthorized Device"
        }), 403

    heart_rate = data["heart_rate"]
    steps = data["steps"]
    temperature = data["temperature"]

    if heart_rate < 30 or heart_rate > 220:
        return jsonify({
            "error": "Invalid heart rate"
        }), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO health_data(
        device_id,
        heart_rate,
        steps,
        temperature,
        created_at
    )
    VALUES(?,?,?,?,?)
    """, (
        device_id,
        heart_rate,
        steps,
        temperature,
        str(datetime.datetime.now())
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Health data stored"
    })

# ------------------------------
# GET DATA
# ------------------------------

@app.route("/api/data")
@jwt_required()
def get_data():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM health_data
    ORDER BY id DESC
    LIMIT 50
    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "device_id": row[1],
            "heart_rate": row[2],
            "steps": row[3],
            "temperature": row[4],
            "time": row[5]
        })

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)