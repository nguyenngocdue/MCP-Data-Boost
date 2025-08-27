from fastmcp import FastMCP
import json, os, threading, sys, logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

app = FastMCP("user-manager")

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
_lock = threading.Lock()

def _ensure_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write("[]")

def _read():
    _ensure_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _write(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.tool()
def listUsers():
    with _lock:
        return _read()

@app.tool()
def createUser(name: str, email: str):
    with _lock:
        users = _read()
        user = {"name": name, "email": email}
        users.append(user)
        _write(users)
        return {"status": "ok", "user": user}

@app.tool()
def updateUser(email: str, name: str = None, newEmail: str = None):
    with _lock:
        users = _read()
        for u in users:
            if u["email"] == email:
                if name is not None: u["name"] = name
                if newEmail is not None: u["email"] = newEmail
                _write(users)
                return {"status": "ok", "user": u}
        return {"status": "not_found", "email": email}

@app.tool()
def deleteUser(email: str):
    with _lock:
        users = _read()
        kept = [u for u in users if u["email"] != email]
        _write(kept)
        return {"status": "ok", "deleted": len(users) - len(kept)}

if __name__ == "__main__":
    app.run_stdio()  # <-- dùng stdin/stdout để giao tiếp với MCPClient
