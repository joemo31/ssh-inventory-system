#!/usr/bin/env python3
"""
SSH Consumables Inventory Management System - Backend API
Flask + SQLite | Port 5050
"""

import sqlite3, hashlib, secrets, json, os
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, g

app = Flask(__name__)
SECRET_KEY = "ssh-inventory-secret-2026"
DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

# ─── DB HELPERS ─────────────────────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db: db.close()

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

def rows_to_list(rows):
    return [dict(r) for r in rows]

# ─── SCHEMA INIT ────────────────────────────────────────────────────────────

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'technician',
        department TEXT,
        initials TEXT,
        active INTEGER DEFAULT 1,
        created_at TEXT 
    );

    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        unit TEXT DEFAULT 'units',
        low_stock_threshold INTEGER DEFAULT 10,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS subtypes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_key TEXT NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY(category_key) REFERENCES categories(key)
    );

    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_key TEXT NOT NULL,
        subtype TEXT,
        date TEXT NOT NULL,
        supplier TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        received_by TEXT,
        remarks TEXT,
        created_by INTEGER,
        created_at TEXT ,
        FOREIGN KEY(category_key) REFERENCES categories(key),
        FOREIGN KEY(created_by) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS issuances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_key TEXT NOT NULL,
        subtype TEXT,
        date TEXT NOT NULL,
        department TEXT,
        received_by TEXT,
        delivered_by TEXT,
        quantity INTEGER NOT NULL,
        on_counter TEXT,
        on_gate TEXT,
        remarks TEXT,
        created_by INTEGER,
        created_at TEXT ,
        FOREIGN KEY(category_key) REFERENCES categories(key),
        FOREIGN KEY(created_by) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        created_at TEXT 
    );
    """)
    db.commit()

    # Seed default data if empty
    cur = db.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        def pw(p): return hashlib.sha256(p.encode()).hexdigest()

        users = [
            ("Mahmoud Ali",    "admin",   pw("admin123"),   "admin",     "IT/Inventory", "MA"),
            ("Sameh El-Sayed", "sameh",   pw("sameh123"),   "engineer",  "Engineering",  "SE"),
            ("Ahmed Nagy",     "ahmed",   pw("ahmed123"),   "technician","Operations",   "AN"),
            ("Yousef",         "yousef",  pw("yousef123"),  "technician","Operations",   "YO"),
            ("Night Reviewer", "night",   pw("night123"),   "reviewer",  "Operations",   "NR"),
        ]
        db.executemany(
            "INSERT INTO users(name,username,password_hash,role,department,initials) VALUES(?,?,?,?,?,?)",
            users
        )

        categories = [
            ("hp80",   "HP 80A Cartridges",       "HP Laser 400 – Black 80A",           "cartridges", 10),
            ("hp59x",  "HP 59X Cartridges",        "HP Laser 404 Pro – White 259X",       "cartridges", 10),
            ("ldcs",   "LDCS Materials",           "Label & Boarding consumables",        "units",       5),
            ("custom", "Custom Printer Heads",     "Custom ATB/BTP heads",               "heads",      10),
            ("dcp",    "DCP Head & Rippon",        "Gate DCP heads and ribbon",           "units",       5),
        ]
        db.executemany(
            "INSERT INTO categories(key,name,description,unit,low_stock_threshold) VALUES(?,?,?,?,?)",
            categories
        )

        subtypes = [
            ("ldcs",  "Label"),
            ("ldcs",  "Boarding"),
            ("dcp",   "Head"),
            ("dcp",   "Rippon"),
        ]
        db.executemany("INSERT INTO subtypes(category_key,name) VALUES(?,?)", subtypes)

        departments = [
            ("BRS",), ("Operations",), ("Baggage Tracking",),
            ("Check-in",), ("Gate Services",), ("Cargo",),
        ]
        db.executemany("INSERT INTO departments(name) VALUES(?)", departments)

        # Seed actual Excel data
        receipts = [
            ("hp80",   None,       "13/04/2026", "In our spare",        5,     None,          None),
            ("hp59x",  None,       "04/08/2026", "In our Spare",        5,     None,          None),
            ("ldcs",   "Label",    "01/01/2026", "Already in our store",5600,  "Mahmoud Ali", None),
            ("ldcs",   "Boarding", "01/01/2026", "Already in our store",25000, "Mahmoud Ali", None),
            ("custom", None,       "04/08/2026", "In our Spare",        44,    None,          None),
            ("dcp",    "Head",     "13/04/2026", "Already in our store",11,    "Mahmoud Ali", None),
            ("dcp",    "Rippon",   "13/04/2026", "Already in our store",19,    "Mahmoud Ali", None),
        ]
        db.executemany(
            "INSERT INTO receipts(category_key,subtype,date,supplier,quantity,received_by,remarks) VALUES(?,?,?,?,?,?,?)",
            receipts
        )

        issuances = [
            ("hp59x", None, "04/08/2026", "BRS", "Ahmed Nagy", "Yousef", 1, None, None, "Mail has been sent"),
        ]
        db.executemany(
            "INSERT INTO issuances(category_key,subtype,date,department,received_by,delivered_by,quantity,on_counter,on_gate,remarks) VALUES(?,?,?,?,?,?,?,?,?,?)",
            issuances
        )

    db.close()

# ─── AUTH ────────────────────────────────────────────────────────────────────

def require_auth(roles=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization","").replace("Bearer ","")
            if not token:
                return jsonify({"error":"Unauthorized"}), 401
            session = query("SELECT s.*,u.id as uid,u.name,u.role,u.username FROM sessions s JOIN users u ON s.user_id=u.id WHERE s.token=?", (token,), one=True)
            if not session:
                return jsonify({"error":"Invalid token"}), 401
            if session["expires_at"] < datetime.now().isoformat():
                return jsonify({"error":"Token expired"}), 401
            if roles and session["role"] not in roles:
                return jsonify({"error":"Forbidden"}), 403
            g.user = dict(session)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

@app.after_request
def after(r): return add_cors(r)

@app.before_request
def options_handler():
    if request.method == "OPTIONS":
        from flask import Response
        r = Response()
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        r.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return r, 200

# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    d = request.json or {}
    username = d.get("username","").strip()
    password = d.get("password","")
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    user = query("SELECT * FROM users WHERE username=? AND password_hash=? AND active=1", (username, pw_hash), one=True)
    if not user:
        return jsonify({"error":"Invalid credentials"}), 401
    token = secrets.token_hex(32)
    expires = (datetime.now() + timedelta(hours=12)).isoformat()
    execute("INSERT INTO sessions(token,user_id,expires_at) VALUES(?,?,?)", (token, user["id"], expires))
    execute("INSERT INTO activity_log(user_id,action,details) VALUES(?,?,?)", (user["id"],"login",f"User {user['name']} logged in"))
    return jsonify({"token":token,"user":{"id":user["id"],"name":user["name"],"role":user["role"],"username":user["username"],"department":user["department"],"initials":user["initials"]}})

@app.route("/api/auth/logout", methods=["POST"])
@require_auth()
def logout():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    execute("DELETE FROM sessions WHERE token=?", (token,))
    return jsonify({"ok":True})

@app.route("/api/auth/me", methods=["GET"])
@require_auth()
def me():
    return jsonify(g.user)

# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@app.route("/api/dashboard", methods=["GET"])
@require_auth()
def dashboard():
    def remaining(cat, subtype=None):
        if subtype:
            recv = query("SELECT COALESCE(SUM(quantity),0) as t FROM receipts WHERE category_key=? AND subtype=?", (cat,subtype), one=True)["t"]
            iss  = query("SELECT COALESCE(SUM(quantity),0) as t FROM issuances WHERE category_key=? AND subtype=?", (cat,subtype), one=True)["t"]
        else:
            recv = query("SELECT COALESCE(SUM(quantity),0) as t FROM receipts WHERE category_key=?", (cat,), one=True)["t"]
            iss  = query("SELECT COALESCE(SUM(quantity),0) as t FROM issuances WHERE category_key=?", (cat,), one=True)["t"]
        return recv - iss

    recent = query("SELECT a.*,u.name as user_name FROM activity_log a LEFT JOIN users u ON a.user_id=u.id ORDER BY a.created_at DESC LIMIT 10")
    cats = rows_to_list(query("SELECT * FROM categories WHERE active=1"))
    thresholds = {c["key"]: c["low_stock_threshold"] for c in cats}

    stock = {
        "hp80":       remaining("hp80"),
        "hp59x":      remaining("hp59x"),
        "ldcs_label": remaining("ldcs","Label"),
        "ldcs_board": remaining("ldcs","Boarding"),
        "custom":     remaining("custom"),
        "dcp_head":   remaining("dcp","Head"),
        "dcp_rippon": remaining("dcp","Rippon"),
    }

    alerts = []
    for k,v in stock.items():
        cat_key = k.split("_")[0]
        thresh = thresholds.get(cat_key, 10)
        if v <= thresh:
            alerts.append({"key":k,"value":v,"threshold":thresh})

    return jsonify({"stock":stock,"alerts":alerts,"recent_activity":rows_to_list(recent)})

# ─── INVENTORY ───────────────────────────────────────────────────────────────

@app.route("/api/inventory/<cat_key>", methods=["GET"])
@require_auth()
def get_inventory(cat_key):
    cat = query("SELECT * FROM categories WHERE key=?", (cat_key,), one=True)
    if not cat: return jsonify({"error":"Not found"}), 404

    receipts = rows_to_list(query("SELECT r.*,u.name as creator_name FROM receipts r LEFT JOIN users u ON r.created_by=u.id WHERE r.category_key=? ORDER BY r.date DESC,r.id DESC", (cat_key,)))
    issuances = rows_to_list(query("SELECT i.*,u.name as creator_name FROM issuances i LEFT JOIN users u ON i.created_by=u.id WHERE i.category_key=? ORDER BY i.date DESC,i.id DESC", (cat_key,)))

    def calc_remaining(subtype=None):
        if subtype:
            r = query("SELECT COALESCE(SUM(quantity),0) as t FROM receipts WHERE category_key=? AND subtype=?", (cat_key,subtype), one=True)["t"]
            i = query("SELECT COALESCE(SUM(quantity),0) as t FROM issuances WHERE category_key=? AND subtype=?", (cat_key,subtype), one=True)["t"]
        else:
            r = query("SELECT COALESCE(SUM(quantity),0) as t FROM receipts WHERE category_key=?", (cat_key,), one=True)["t"]
            i = query("SELECT COALESCE(SUM(quantity),0) as t FROM issuances WHERE category_key=?", (cat_key,), one=True)["t"]
        return r - i

    subtypes = rows_to_list(query("SELECT * FROM subtypes WHERE category_key=?", (cat_key,)))
    remaining = {}
    if subtypes:
        for st in subtypes:
            remaining[st["name"]] = calc_remaining(st["name"])
    else:
        remaining["total"] = calc_remaining()

    return jsonify({"category":dict(cat),"receipts":receipts,"issuances":issuances,"remaining":remaining,"subtypes":[s["name"] for s in subtypes]})

# ─── RECEIPTS ────────────────────────────────────────────────────────────────

@app.route("/api/receipts", methods=["POST"])
@require_auth(roles=["admin","engineer","technician","reviewer"])
def add_receipt():
    d = request.json or {}
    required = ["category_key","date","supplier","quantity"]
    for f in required:
        if not d.get(f): return jsonify({"error":f"Missing {f}"}), 400

    rid = execute(
        "INSERT INTO receipts(category_key,subtype,date,supplier,quantity,received_by,remarks,created_by) VALUES(?,?,?,?,?,?,?,?)",
        (d["category_key"], d.get("subtype"), d["date"], d["supplier"], int(d["quantity"]), d.get("received_by"), d.get("remarks"), g.user["uid"])
    )
    execute("INSERT INTO activity_log(user_id,action,details) VALUES(?,?,?)",
        (g.user["uid"], "receipt",
         f"Received {d['quantity']} {d['category_key']}{' '+d['subtype'] if d.get('subtype') else ''} from {d['supplier']}"))
    return jsonify({"id":rid,"ok":True})

@app.route("/api/receipts/<int:rid>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_receipt(rid):
    execute("DELETE FROM receipts WHERE id=?", (rid,))
    return jsonify({"ok":True})

# ─── ISSUANCES ───────────────────────────────────────────────────────────────

@app.route("/api/issuances", methods=["POST"])
@require_auth(roles=["admin","engineer","technician","reviewer"])
def add_issuance():
    d = request.json or {}
    required = ["category_key","date","quantity"]
    for f in required:
        if not d.get(f): return jsonify({"error":f"Missing {f}"}), 400

    # Stock check
    cat_key = d["category_key"]
    subtype = d.get("subtype")
    if subtype:
        recv = query("SELECT COALESCE(SUM(quantity),0) as t FROM receipts WHERE category_key=? AND subtype=?", (cat_key,subtype), one=True)["t"]
        iss  = query("SELECT COALESCE(SUM(quantity),0) as t FROM issuances WHERE category_key=? AND subtype=?", (cat_key,subtype), one=True)["t"]
    else:
        recv = query("SELECT COALESCE(SUM(quantity),0) as t FROM receipts WHERE category_key=?", (cat_key,), one=True)["t"]
        iss  = query("SELECT COALESCE(SUM(quantity),0) as t FROM issuances WHERE category_key=?", (cat_key,), one=True)["t"]
    remaining = recv - iss
    if int(d["quantity"]) > remaining:
        return jsonify({"error":f"Insufficient stock. Available: {remaining}"}), 400

    iid = execute(
        "INSERT INTO issuances(category_key,subtype,date,department,received_by,delivered_by,quantity,on_counter,on_gate,remarks,created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (cat_key, subtype, d["date"], d.get("department"), d.get("received_by"),
         d.get("delivered_by"), int(d["quantity"]), d.get("on_counter"), d.get("on_gate"),
         d.get("remarks"), g.user["uid"])
    )
    execute("INSERT INTO activity_log(user_id,action,details) VALUES(?,?,?)",
        (g.user["uid"], "issuance",
         f"Issued {d['quantity']} {cat_key}{' '+subtype if subtype else ''} to {d.get('department','-')}"))
    return jsonify({"id":iid,"ok":True})

@app.route("/api/issuances/<int:iid>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_issuance(iid):
    execute("DELETE FROM issuances WHERE id=?", (iid,))
    return jsonify({"ok":True})

# ─── CATEGORIES ──────────────────────────────────────────────────────────────

@app.route("/api/categories", methods=["GET"])
@require_auth()
def get_categories():
    cats = rows_to_list(query("SELECT * FROM categories WHERE active=1"))
    for c in cats:
        c["subtypes"] = [r["name"] for r in query("SELECT name FROM subtypes WHERE category_key=?", (c["key"],))]
    return jsonify(cats)

@app.route("/api/categories/<key>/threshold", methods=["PUT"])
@require_auth(roles=["admin"])
def update_threshold(key):
    d = request.json or {}
    execute("UPDATE categories SET low_stock_threshold=? WHERE key=?", (int(d.get("threshold",10)), key))
    return jsonify({"ok":True})

# ─── USERS ───────────────────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
@require_auth(roles=["admin"])
def get_users():
    users = rows_to_list(query("SELECT id,name,username,role,department,initials,active,created_at FROM users"))
    return jsonify(users)

@app.route("/api/users", methods=["POST"])
@require_auth(roles=["admin"])
def create_user():
    d = request.json or {}
    pw_hash = hashlib.sha256(d.get("password","pass123").encode()).hexdigest()
    uid = execute(
        "INSERT INTO users(name,username,password_hash,role,department,initials) VALUES(?,?,?,?,?,?)",
        (d["name"], d["username"], pw_hash, d.get("role","technician"), d.get("department"), d.get("initials",""))
    )
    return jsonify({"id":uid,"ok":True})

@app.route("/api/users/<int:uid>", methods=["PUT"])
@require_auth(roles=["admin"])
def update_user(uid):
    d = request.json or {}
    execute("UPDATE users SET name=?,role=?,department=?,active=? WHERE id=?",
        (d.get("name"), d.get("role"), d.get("department"), int(d.get("active",1)), uid))
    return jsonify({"ok":True})

@app.route("/api/users/<int:uid>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_user(uid):
    execute("UPDATE users SET active=0 WHERE id=?", (uid,))
    return jsonify({"ok":True})

# ─── DEPARTMENTS ─────────────────────────────────────────────────────────────

@app.route("/api/departments", methods=["GET"])
@require_auth()
def get_departments():
    return jsonify(rows_to_list(query("SELECT * FROM departments ORDER BY name")))

@app.route("/api/departments", methods=["POST"])
@require_auth(roles=["admin"])
def add_department():
    d = request.json or {}
    did = execute("INSERT OR IGNORE INTO departments(name) VALUES(?)", (d["name"],))
    return jsonify({"id":did,"ok":True})

@app.route("/api/departments/<int:did>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_department(did):
    execute("DELETE FROM departments WHERE id=?", (did,))
    return jsonify({"ok":True})

# ─── REPORTS ─────────────────────────────────────────────────────────────────

@app.route("/api/reports/monthly", methods=["GET"])
@require_auth(roles=["admin","engineer"])
def monthly_report():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    start = f"{month}-01"
    # Get end of month
    y, m = int(month.split("-")[0]), int(month.split("-")[1])
    if m == 12: end = f"{y+1}-01-01"
    else: end = f"{y}-{m+1:02d}-01"

    receipts = rows_to_list(query(
        "SELECT r.*,c.name as cat_name FROM receipts r JOIN categories c ON r.category_key=c.key WHERE r.date>=? AND r.date<? ORDER BY r.date",
        (start, end)
    ))
    issuances = rows_to_list(query(
        "SELECT i.*,c.name as cat_name FROM issuances i JOIN categories c ON i.category_key=c.key WHERE i.date>=? AND i.date<? ORDER BY i.date",
        (start, end)
    ))

    return jsonify({"month":month,"receipts":receipts,"issuances":issuances,
                    "totals":{"received":sum(r["quantity"] for r in receipts),
                              "issued":sum(i["quantity"] for i in issuances)}})

@app.route("/api/activity", methods=["GET"])
@require_auth()
def get_activity():
    limit = int(request.args.get("limit", 20))
    logs = rows_to_list(query("SELECT a.*,u.name as user_name FROM activity_log a LEFT JOIN users u ON a.user_id=u.id ORDER BY a.created_at DESC LIMIT ?", (limit,)))
    return jsonify(logs)

# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized")
    print("🚀 SSH Inventory API running on http://localhost:5050")
    print("\nDefault users:")
    print("  admin / admin123  (Administrator)")
    print("  sameh / sameh123  (Engineer)")
    print("  ahmed / ahmed123  (Technician)")
    print("  yousef / yousef123 (Technician)")
    app.run(host="0.0.0.0", port=5050, debug=False)
