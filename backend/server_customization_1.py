from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os, json, threading
from mcp_use import MCPAgent, MCPClient
import random






# ---------- Config ----------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USERS_JSON     = os.path.abspath(os.getenv("USERS_JSON", "./data/users.json"))
FRONTEND_ORIGIN= os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

def generate_random_name():
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_email(name: str):
    domains = ["example.com", "test.org", "demo.net", "mail.io"]
    clean_name = name.replace(" ", "").lower()
    return f"{clean_name}{random.randint(100, 999)}@{random.choice(domains)}"

def read_users():
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def write_users(users):
    with open(USERS_JSON, "w", encoding="utf-8") as f:
        json.dump( users, f, ensure_ascii=False, indent=2)

def next_id(users):
    return (max([u["id"] for u in users], default=0) + 1)

_next_id = max(user["id"] for user in read_users())  + 1 
def get_next_id():
    global _next_id
    current = _next_id
    _next_id += 1
    return current


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
    # "Convert Vietnamese/English user requests into a strict JSON command.\n"
    # "Allowed actions: create, update, delete, list, none, bulk_create, bulk_create_random. Output ONLY JSON.\n"
    # 'If the request is unrelated to user CRUD, return {"action":"none","reason":"..."}.\n'
    # 'Schema: {\n'
    # '  "action": "create|update|delete|list|bulk_create|bulk_create_random|none",\n'
    # '  "id": int?,\n'
    # '  "name": str?,\n'
    # '  "email": str?,\n'
    # '  "count": int?,  // Required when action is bulk_create or bulk_create_random\n'
    # '  "reason": str?\n'
    # '}\n'
    # '\n'
    # '--- Examples ---\n'
    # 'Ex1 IN: "create a new user named Minh, email minh@example.com"\n'
    # 'Ex1 OUT: {"action":"create","name":"Minh","email":"minh@example.com"}\n'
    # '\n'
    # 'Ex2 IN: "delete user with id 3"\n'
    # 'Ex2 OUT: {"action":"delete","id":3}\n'
    # '\n'
    # 'Ex3 IN: "update user 2: name Nam, email nam@abc.com"\n'
    # 'Ex3 OUT: {"action":"update","id":2,"name":"Nam","email":"nam@abc.com"}\n'
    # '\n'
    # 'Ex4 IN: "list all users"\n'
    # 'Ex4 OUT: {"action":"list"}\n'
    # '\n'
    # 'Ex5 IN: "what is the weather today?"\n'
    # 'Ex5 OUT: {"action":"none","reason":"Question not related to user management"}\n'
    # '\n'
    # 'Ex6 IN: "create 5 users named Dev"\n'
    # 'Ex6 OUT: {"action":"bulk_create","name":"Dev","count":5}\n'
    # '\n'
    # 'Ex7 IN: "tạo 3 người dùng ngẫu nhiên"\n'
    # 'Ex7 OUT: {"action":"bulk_create_random","count":3}\n'
    # '\n'
    # 'Ex8 IN: "create 10 random users"\n'
    # 'Ex8 OUT: {"action":"bulk_create_random","count":10}\n'
    # '\n'
    # 'Ex9 IN: "make 2 random testers"\n'
    # 'Ex9 OUT: {"action":"bulk_create_random","count":2}\n'
    # '\n'
    '⚠️ Note: Only output valid JSON. No extra text.'
)


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
        print(f"NL ------------------------> JSON: {resp.content}")
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
        return await run_query(req)

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

        elif action == "bulk_create_random":
            count = cmd.get("count")
            if not isinstance(count, int) or count < 1:
                raise HTTPException(status_code=400, detail="bulk_create_random requires positive integer count")
            created_users = []
            for _ in range(count):
                name = generate_random_name()
                email = generate_random_email(name)
                uid = get_next_id()  
                user = {"id": uid, "name": name, "email": email}
                users.append(user)
                created_users.append(user)

            write_users(users)  # lưu danh sách
            return {
                "ok": True,
                "mode": "crud",
                "action": "bulk_create_random",
                "count": count,
                "user": created_users
            }
        
    # If the action is not valid
    raise HTTPException(status_code=400, detail="Unknown action or invalid request")


async def run_query(req: Request):
    # Create MCP client from the configuration
    client = MCPClient.from_config_file("multi_server_config.json")
    # Create the LLM (Large Language Model) interface using OpenAI
    llm = ChatOpenAI(model=OPENAI_MODEL)
    # Parse JSON request body
    body = await req.json()
    q = body.get("query", "")
    steps = int(body.get("max_steps", 30))

    print(f"[API] =======> query={q!r}, steps={steps}")
    try:
        # Create an MCP agent with LLM + MCP client
        agent = MCPAgent(llm=llm, client=client, max_steps=steps
                        , use_server_manager=True  # Enable the Server Manager
                    )
        
        # Run the query using the agent (LLM + Playwright MCP)
        result = await agent.run(q, max_steps=steps)

        print("[API] done")
        return {"result": result}
    except Exception as e:
        # Print error to console and return 500 response
        print("[API] ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/health")
def health():
    return {"ok": True, "model": OPENAI_MODEL, "file": USERS_JSON}
