from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os, json, threading

# ---------- Config ----------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USERS_JSON     = os.path.abspath(os.getenv("USERS_JSON", "./data/users.json"))
FRONTEND_ORIGIN= os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

os.makedirs(os.path.dirname(USERS_JSON), exist_ok=True)
if not os.path.exists(USERS_JSON):
    with open(USERS_JSON, "w", encoding="utf-8") as f:
        json.dump({"users": []}, f, ensure_ascii=False, indent=2)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model  = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
_lock = threading.Lock()

SYSTEM_PROMPT = (
    "Convert Vietnamese/English user requests into a strict JSON command.\n"
    "Allowed actions: create, update, delete, list, none. Output ONLY JSON.\n"
    'If the request is unrelated to user CRUD, return {"action":"none","reason":"..."}.\n'
    'Schema: {"action":"create|update|delete|list|none","id":int?,"name":str?,"email":str?,"reason":str?}\n'
    'Ex1 IN: "create a new user named Minh, email minh@example.com"\n'
    'Ex1 OUT: {"action":"create","name":"Minh","email":"minh@example.com"}\n'
    'Ex2 IN: "delete user with id 3"\n'
    'Ex2 OUT: {"action":"delete","id":3}\n'
    'Ex3 IN: "update user 2: name Nam, email nam@abc.com"\n'
    'Ex3 OUT: {"action":"update","id":2,"name":"Nam","email":"nam@abc.com"}\n'
    'Ex4 IN: "list all users"\n'
    'Ex4 OUT: {"action":"list"}\n'
    'Ex5 IN: "what is the weather today?"\n'
    'Ex5 OUT: {"action":"none","reason":"Question not related to user management"}'
)

def read_users():
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def write_users(users):
    with open(USERS_JSON, "w", encoding="utf-8") as f:
        json.dump( users, f, ensure_ascii=False, indent=2)

def next_id(users):
    return (max([u["id"] for u in users], default=0) + 1)

@app.get("/api/users")
def get_users():
    return  read_users()

@app.post("/api/users/nl")
async def users_nl(req: Request):
    body = await req.json()
    q = (body.get("query") or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Missing 'query'")

    # 1) NL -> JSON command attempt
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": q}
    ]
    try:
        resp = await model.ainvoke(msgs)
        raw  = (resp.content or "").strip()
        cmd  = json.loads(raw)
    except Exception:
        # ❌ If parsing JSON fails → fallback to chat
        chat_resp = await model.ainvoke([{"role": "user", "content": q}])
        return {
            "ok": True,
            "mode": "chat",
            "answer": chat_resp.content
        }

    # 2) If parsing is successful → check the action
    action = cmd.get("action")

    # 🔁 If the action is "none" → use the model to respond freely
    if action == "none":
        reason = cmd.get("reason", "No reason provided")
        # Either use the reason, or ignore and ask the model again
        chat_resp = await model.ainvoke([{"role": "user", "content": q}])
        return {
            "ok": True,
            "mode": "chat",
            "answer": chat_resp.content
        }

    # 3) Handle CRUD actions (keeping the previous code)
    with _lock:
        users = read_users()

        if action == "list":
            return {"ok": True, "mode": "crud", "action": "list", "users": users}

        if action == "create":
            name  = (cmd.get("name") or "").strip()
            email = (cmd.get("email") or "").strip()
            if not name or not email:
                raise HTTPException(status_code=400, detail="create requires name & email")
            if any(u["email"].lower() == email.lower() for u in users):
                raise HTTPException(status_code=409, detail="Email already exists")
            user = {"id": next_id(users), "name": name, "email": email}
            users.append(user)
            write_users(users)
            return {"ok": True, "mode": "crud", "action": "create", "user": user}

        if action == "update":
            uid = cmd.get("id")
            if not uid:
                raise HTTPException(status_code=400, detail="update requires id")
            for u in users:
                if u["id"] == uid:
                    name = (cmd.get("name") or u["name"]).strip()
                    email = (cmd.get("email") or u["email"]).strip()
                    if email.lower() != u["email"].lower() and any(x["email"].lower() == email.lower() for x in users):
                        raise HTTPException(status_code=409, detail="Email already exists")
                    u["name"], u["email"] = name, email
                    write_users(users)
                    return {"ok": True, "mode": "crud", "action": "update", "user": u}
            raise HTTPException(status_code=404, detail="User not found")

        if action == "delete":
            uid = cmd.get("id")
            if not uid:
                raise HTTPException(status_code=400, detail="delete requires id")
            for i, u in enumerate(users):
                if u["id"] == uid:
                    deleted = users.pop(i)
                    write_users(users)
                    return {"ok": True, "mode": "crud", "action": "delete", "user": deleted}
            raise HTTPException(status_code=404, detail="User not found")

    # If the action is not valid
    raise HTTPException(status_code=400, detail="Unknown action or invalid request")


@app.get("/health")
def health():
    return {"ok": True, "model": OPENAI_MODEL, "file": USERS_JSON}
